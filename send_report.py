import smtplib
import os
import sys
import json
import glob
import re
import base64
import socket
import platform
import subprocess
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv

load_dotenv()

for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError, AttributeError, TypeError):
            pass

_EXTRA_REPORT_RECEIVERS = ()

# 功能 → 大分類 對應表
_FEATURE_CATEGORY = {
    "PC版官網登入頁":       "🔑 登入測試",
    "共登PC-帳密登入":      "🔑 登入測試",
    "共登PC-Gama Pass登入": "🔑 登入測試",
    "OPEN ID 登入":         "🔑 登入測試",
    "會員登入功能":         "🔑 登入測試",
    "PC版官網首頁功能驗證": "🖥️ PC 版測試",
    "PC版官網右側功能列":   "🖥️ PC 版測試",
    "PC版官網會員中心":     "🖥️ PC 版測試",
    "PC版官網會員中心側欄": "🖥️ PC 版測試",
    "PC版官網儲值與購點":   "🖥️ PC 版測試",
    "PC版官網客服中心":     "🖥️ PC 版測試",
}
_CATEGORY_ORDER = ["🔑 登入測試", "🖥️ PC 版測試"]

_FEATURE_ORDER = [
    "PC版官網登入頁",
    "共登PC-帳密登入",
    "共登PC-Gama Pass登入",
    "OPEN ID 登入",
    "會員登入功能",
    "PC版官網首頁功能驗證",
    "PC版官網右側功能列",
    "PC版官網會員中心",
    "PC版官網會員中心側欄",
    "PC版官網儲值與購點",
    "PC版官網客服中心",
]


def _log(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(msg.encode(enc, errors="replace").decode(enc, errors="replace"))


def _parse_receiver_list(raw: str) -> list[str]:
    out: list[str] = []
    for part in raw.replace(";", ",").split(","):
        addr = part.strip()
        if addr:
            out.append(addr)
    return out


def _is_credentials_skip(message: str) -> bool:
    return "BEANFUN_" in message and ("缺少" in message or "請設定" in message)


def _mask_email(addr: str) -> str:
    if not addr or "@" not in addr:
        return "(無效或未設定)"
    local, domain = addr.strip().split("@", 1)
    masked = local[0] + "***" + local[-1] if len(local) > 1 else "*" * min(3, max(1, len(local)))
    return f"{masked}@{domain}"


def _get_chrome_version() -> str:
    keys = [
        r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon",
    ]
    for key in keys:
        try:
            result = subprocess.run(
                ["reg", "query", key, "/v", "version"],
                capture_output=True, text=True, timeout=5,
            )
            m = re.search(r"version\s+REG_SZ\s+([\d.]+)", result.stdout, re.IGNORECASE)
            if m:
                return m.group(1)
        except Exception:
            continue
    return "未知"


def _get_timing(results_dir: str) -> tuple[int | None, int | None]:
    min_start: int | None = None
    max_stop:  int | None = None
    for jf in glob.glob(os.path.join(results_dir, "*-result.json")):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                d = json.load(f)
            s, e = d.get("start"), d.get("stop")
            if s and (min_start is None or s < min_start):
                min_start = s
            if e and (max_stop is None or e > max_stop):
                max_stop = e
        except Exception:
            continue
    return min_start, max_stop


def _pick_local_report_html(base_dir: str) -> tuple[str, bool]:
    history_dir = os.path.join(base_dir, "HistoryReports")
    if os.path.isdir(history_dir):
        snapshots = sorted(
            glob.glob(os.path.join(history_dir, "Report_*.html")),
            reverse=True,
        )
        if snapshots:
            return snapshots[0], True

    rd         = os.path.join(base_dir, "allure-report")
    complete   = os.path.join(rd, "complete.html")
    index_html = os.path.join(rd, "index.html")
    if os.path.isfile(complete):
        return complete, True
    if os.path.isfile(index_html):
        return index_html, True
    return complete, False


def _load_features(results_dir: str) -> tuple[dict, dict, float]:
    summary_data: dict = {"total": 0, "passed": 0, "failed": 0, "locked": 0}
    json_files = glob.glob(os.path.join(results_dir, "*-result.json"))
    if not json_files:
        return {}, summary_data, 0.0

    _dedup: dict = {}
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            feature_name = "未分類功能測試"
            for label in data.get("labels", []):
                if label["name"] == "feature":
                    feature_name = label["value"]
            full_name  = data.get("fullName") or data.get("name", "")
            dedup_key  = (feature_name, full_name)
            stop_ts    = data.get("stop", 0)
            if dedup_key in _dedup and stop_ts <= _dedup[dedup_key].get("stop", 0):
                continue
            _dedup[dedup_key] = data
        except Exception:
            continue

    features: dict = {}
    for (feature_name, _), data in _dedup.items():
        status       = data.get("status", "")
        skip_message = data.get("statusDetails", {}).get("message", "")
        if status == "skipped" and _is_credentials_skip(skip_message):
            continue
        summary_data["total"] += 1
        if status == "passed":
            summary_data["passed"] += 1
        elif status == "skipped":
            summary_data["locked"] += 1
        else:
            summary_data["failed"] += 1
        features.setdefault(feature_name, []).append(data)

    success_rate = (
        summary_data["passed"] / summary_data["total"] * 100
        if summary_data["total"] > 0 else 0.0
    )
    return features, summary_data, success_rate


def _format_test_name(raw: str) -> str:
    return raw.replace("：", ": ")


def _img_to_b64(path: str) -> str | None:
    """PNG 檔案轉 base64 data URI，失敗回傳 None。"""
    try:
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    except Exception:
        return None


def _steps_html(steps: list, results_dir: str, level: int = 0) -> str:
    """遞迴將 Allure steps 轉成 HTML，並內嵌截圖（base64）。"""
    _STATUS_STYLE = {
        "passed":  ("✅", "#e8f5e9", "#2e7d32"),
        "failed":  ("❌", "#ffebee", "#c62828"),
        "broken":  ("💥", "#ffebee", "#c62828"),
        "skipped": ("⚠️", "#fffde7", "#f57f17"),
    }
    pad = 16 + level * 20
    html = ""
    for i, step in enumerate(steps, 1):
        st = step.get("status", "unknown")
        icon, bg, fg = _STATUS_STYLE.get(st, ("•", "#f5f5f5", "#777"))

        name = step.get("name", "").strip()
        name = re.sub(r"^步驟\s*\d+\s*:\s*", "", name)
        name = re.sub(r"^\d+\.\s*", "", name)

        ss_html = ""
        for att in step.get("attachments", []):
            if att.get("type") == "image/png":
                b64 = _img_to_b64(os.path.join(results_dir, att["source"]))
                if b64:
                    ss_html = (
                        f'<details style="display:inline-block;vertical-align:top;margin-left:10px;">'
                        f'<summary style="cursor:pointer;font-size:11px;color:#1565c0;'
                        f'background:#e3f2fd;padding:1px 6px;border-radius:3px;">📸 截圖</summary>'
                        f'<div style="margin-top:4px;">'
                        f'<img src="{b64}" style="max-width:540px;border:1px solid #bbb;'
                        f'border-radius:3px;display:block;"></div>'
                        f'</details>'
                    )
                break

        html += (
            f'<div style="padding:4px 8px 4px {pad}px;background:{bg};'
            f'color:{fg};font-size:13px;border-bottom:1px solid rgba(0,0,0,0.05);">'
            f'{icon} {i}. {name}{ss_html}'
            f'</div>\n'
        )

        sub = step.get("steps", [])
        if sub:
            html += _steps_html(sub, results_dir, level + 1)

    return html


def _feat_pass_count(tests: list) -> tuple[int, int]:
    passed = sum(1 for t in tests if t.get("status") == "passed")
    return passed, len(tests)


def _build_accordion_html(
    features: dict,
    summary: dict,
    success_rate: float,
    start_str: str,
    end_str: str,
    elapsed: float,
    chrome_ver: str,
    hostname: str,
    ip: str,
    os_name: str,
    status_text: str,
    results_dir: str,
    report_path: str,
    report_file_ok: bool,
) -> str:
    """產生 HTML 手風琴測試報告（含 base64 內嵌截圖）。"""

    rate_color = (
        "#2e7d32" if success_rate >= 90
        else ("#f57f17" if success_rate >= 70 else "#c62828")
    )

    # ── 頁首 + 環境資訊 ─────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="zh-TW"><head><meta charset="utf-8">
<style>
  details > summary {{ list-style: none; }}
  details > summary::-webkit-details-marker {{ display: none; }}
  details[open] > summary .arr {{ transform: rotate(90deg); }}
  .arr {{ display:inline-block; transition:transform .2s; }}
</style>
</head>
<body style="font-family:Arial,'Microsoft JhengHei',sans-serif;font-size:14px;
             color:#333;max-width:960px;margin:0 auto;padding:20px;">

<h2 style="color:#1565c0;border-bottom:3px solid #1565c0;padding-bottom:10px;margin-bottom:16px;">
  📋 官網自動化測試報告
</h2>

<!-- 環境資訊 -->
<table style="width:100%;border-collapse:collapse;margin-bottom:16px;font-size:13px;
              border:1px solid #e0e0e0;border-radius:4px;">
  <tr style="background:#1565c0;color:white;">
    <th colspan="2" style="padding:8px 12px;text-align:left;">🖥️ 測試環境資訊</th>
  </tr>
  <tr>
    <td style="padding:5px 12px;color:#555;width:140px;border-bottom:1px solid #f0f0f0;">執行時間</td>
    <td style="padding:5px 12px;border-bottom:1px solid #f0f0f0;">{start_str} ～ {end_str}</td>
  </tr>
  <tr style="background:#f9f9f9;">
    <td style="padding:5px 12px;color:#555;border-bottom:1px solid #f0f0f0;">耗時</td>
    <td style="padding:5px 12px;border-bottom:1px solid #f0f0f0;">{elapsed:.1f} 秒</td>
  </tr>
  <tr>
    <td style="padding:5px 12px;color:#555;border-bottom:1px solid #f0f0f0;">測試裝置</td>
    <td style="padding:5px 12px;border-bottom:1px solid #f0f0f0;">{os_name} + Chrome (Headless) {chrome_ver}</td>
  </tr>
  <tr style="background:#f9f9f9;">
    <td style="padding:5px 12px;color:#555;border-bottom:1px solid #f0f0f0;">網路環境</td>
    <td style="padding:5px 12px;border-bottom:1px solid #f0f0f0;">{hostname} / {ip}</td>
  </tr>
  <tr>
    <td style="padding:5px 12px;color:#555;">測試框架</td>
    <td style="padding:5px 12px;">pytest + Selenium WebDriver</td>
  </tr>
</table>

<!-- 統計摘要 -->
<table style="width:100%;border-collapse:collapse;margin-bottom:20px;
              border:1px solid #e0e0e0;font-size:14px;">
  <tr style="background:#1565c0;color:white;">
    <th colspan="4" style="padding:8px 12px;text-align:left;">📊 測試統計摘要</th>
  </tr>
  <tr style="text-align:center;background:#f9f9f9;">
    <td style="padding:10px;border:1px solid #e0e0e0;">
      <div style="font-size:22px;font-weight:bold;">{summary['total']}</div>
      <div style="font-size:11px;color:#777;">總測試數</div>
    </td>
    <td style="padding:10px;border:1px solid #e0e0e0;color:#2e7d32;">
      <div style="font-size:22px;font-weight:bold;">✅ {summary['passed']}</div>
      <div style="font-size:11px;color:#777;">通過</div>
    </td>
    <td style="padding:10px;border:1px solid #e0e0e0;color:#c62828;">
      <div style="font-size:22px;font-weight:bold;">❌ {summary['failed']}</div>
      <div style="font-size:11px;color:#777;">失敗</div>
    </td>
    <td style="padding:10px;border:1px solid #e0e0e0;color:#f57f17;">
      <div style="font-size:22px;font-weight:bold;">⚠️ {summary['locked']}</div>
      <div style="font-size:11px;color:#777;">跳過/鎖定</div>
    </td>
  </tr>
  <tr>
    <td colspan="4" style="text-align:center;padding:12px;font-size:18px;font-weight:bold;
                            color:{rate_color};border:1px solid #e0e0e0;">
      成功率：{success_rate:.1f}%　{status_text}
    </td>
  </tr>
</table>

<h3 style="color:#1565c0;border-bottom:1px solid #bbdefb;padding-bottom:6px;">📝 詳細測試結果</h3>
"""

    # ── 手風琴主體 ──────────────────────────────────────────
    ordered_feats = [f for f in _FEATURE_ORDER if f in features] + \
                    [f for f in features if f not in _FEATURE_ORDER]

    categories: dict[str, list[str]] = {}
    for feat in ordered_feats:
        cat = _FEATURE_CATEGORY.get(feat, "📋 其他測試")
        categories.setdefault(cat, []).append(feat)

    cat_order = _CATEGORY_ORDER + [c for c in categories if c not in _CATEGORY_ORDER]

    for cat in cat_order:
        if cat not in categories:
            continue

        cat_feats = categories[cat]
        cat_total = sum(len(features[f]) for f in cat_feats)
        cat_pass  = sum(
            sum(1 for t in features[f] if t.get("status") == "passed")
            for f in cat_feats
        )
        cat_has_fail = any(
            any(t.get("status") not in ("passed", "skipped") for t in features[f])
            for f in cat_feats
        )
        cat_hdr_bg = "#c62828" if cat_has_fail else "#2e7d32"

        html += f"""
<details open style="margin-bottom:10px;border:1px solid #ddd;border-radius:5px;overflow:hidden;">
  <summary style="padding:10px 14px;background:{cat_hdr_bg};color:white;
                  cursor:pointer;font-weight:bold;font-size:15px;">
    <span class="arr">▶</span> {cat} &nbsp; [{cat_pass}/{cat_total}]
  </summary>
  <div style="padding:10px;">
"""

        for feat in cat_feats:
            tests = sorted(features[feat], key=lambda t: t.get("name", ""))
            f_pass, f_total = _feat_pass_count(tests)
            f_has_fail = any(t.get("status") not in ("passed", "skipped") for t in tests)
            f_bg = "#fff3e0" if f_has_fail else "#f1f8e9"
            f_border = "#e65100" if f_has_fail else "#558b2f"

            html += f"""
    <details style="margin-bottom:8px;border:1px solid {f_border};border-radius:4px;overflow:hidden;">
      <summary style="padding:7px 12px;background:{f_bg};cursor:pointer;
                      font-weight:bold;font-size:14px;border-left:4px solid {f_border};">
        <span class="arr">▶</span> 【{feat}】&nbsp; [{f_pass}/{f_total}]
      </summary>
      <div style="padding:6px 0;">
"""

            for test in tests:
                st     = test.get("status", "")
                t_name = _format_test_name(test.get("name", "").strip())
                msg    = test.get("statusDetails", {}).get("message", "")

                if st == "passed":
                    t_bg, t_fg, t_icon, t_open = "#e8f5e9", "#2e7d32", "✅", ""
                elif st == "skipped":
                    t_bg, t_fg, t_icon, t_open = "#fffde7", "#f57f17", "⚠️", ""
                else:
                    t_bg, t_fg, t_icon, t_open = "#ffebee", "#c62828", "❌", " open"

                html += f"""
        <details{t_open} style="margin:5px 10px;border:1px solid #e0e0e0;border-radius:3px;overflow:hidden;">
          <summary style="padding:6px 10px;background:{t_bg};color:{t_fg};
                          cursor:pointer;font-size:13px;font-weight:bold;">
            <span class="arr">▶</span> {t_icon} {t_name}
          </summary>
          <div style="background:#fff;">
"""

                if st == "skipped":
                    reason = msg.strip().split("\n")[0] if msg else "環境限制"
                    html += (
                        f'<div style="padding:6px 20px;color:#f57f17;font-size:12px;">'
                        f'原因：{reason}</div>\n'
                    )
                else:
                    steps = test.get("steps", [])
                    if steps:
                        html += _steps_html(steps, results_dir)
                    elif st != "passed" and msg:
                        escaped = msg.strip()[:400].replace("<", "&lt;").replace(">", "&gt;")
                        html += (
                            f'<div style="padding:6px 20px;color:#c62828;'
                            f'font-size:12px;font-family:monospace;">{escaped}</div>\n'
                        )

                html += "          </div>\n        </details>\n"

            html += "      </div>\n    </details>\n"

        html += "  </div>\n</details>\n"

    # ── 頁尾 ────────────────────────────────────────────────
    report_note = (
        f'📁 <code style="font-size:12px;color:#1565c0;">{report_path}</code>'
        if report_file_ok
        else f'⚠️ 找不到報告檔，預期路徑：<code style="font-size:12px;">{report_path}</code>'
    )

    html += f"""
<p style="margin-top:24px;color:#999;font-size:12px;
          border-top:1px solid #eee;padding-top:12px;line-height:1.8;">
  {report_note}<br>
  自動化機器人 敬上
</p>

</body></html>"""

    return html


def send_email() -> None:
    sender_email    = (os.getenv("REPORT_SENDER_EMAIL") or "").strip()
    sender_password = (os.getenv("REPORT_SENDER_PWD") or "").strip()
    receiver_raw    = (os.getenv("REPORT_RECEIVER_EMAIL") or "").strip()
    receivers = _parse_receiver_list(receiver_raw)
    seen_lower = {r.lower() for r in receivers}
    for extra in _EXTRA_REPORT_RECEIVERS:
        if extra.lower() not in seen_lower:
            receivers.append(extra)
            seen_lower.add(extra.lower())

    if not sender_email or not sender_password:
        _log("[send_report] 錯誤：找不到 .env 中的 REPORT_SENDER_EMAIL / REPORT_SENDER_PWD。")
        return
    if not receivers:
        _log("[send_report] 錯誤：.env 缺少 REPORT_RECEIVER_EMAIL（收件信箱）。")
        return

    base_dir     = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(base_dir, "allure-results")
    report_html_path, report_file_ok = _pick_local_report_html(base_dir)

    _log("[send_report] 正在讀取測試結果...")
    features, summary, success_rate = _load_features(results_path)

    # ── 環境資訊 ──────────────────────────────────────────────
    min_ts, max_ts = _get_timing(results_path)
    start_str = datetime.fromtimestamp(min_ts / 1000).strftime("%Y-%m-%d %H:%M:%S") if min_ts else "N/A"
    end_str   = datetime.fromtimestamp(max_ts / 1000).strftime("%Y-%m-%d %H:%M:%S") if max_ts else "N/A"
    elapsed   = (max_ts - min_ts) / 1000 if (min_ts and max_ts) else 0.0

    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "N/A"

    chrome_ver  = _get_chrome_version()
    os_name     = f"Windows {platform.release()}"
    status_text = (
        "✅ 全部通過" if summary["failed"] == 0 and summary["locked"] == 0
        else ("❌ 有失敗項目" if summary["failed"] > 0 else "⚠️ 有鎖定項目")
    )

    # ── 郵件主旨 ──────────────────────────────────────────────
    status_icon = "✅" if summary["failed"] == 0 and summary["locked"] == 0 else "❌"
    subject = f"{status_icon} 官網自動化測試摘要 - 成功率: {success_rate:.0f}%"

    # ── 產生 HTML 報告 ─────────────────────────────────────────
    if features:
        html_body = _build_accordion_html(
            features, summary, success_rate,
            start_str, end_str, elapsed,
            chrome_ver, hostname, ip, os_name, status_text,
            results_path, report_html_path, report_file_ok,
        )
    else:
        html_body = "<p>⚠️ 找不到任何測試結果。</p>"

    msg = MIMEMultipart()
    msg["From"]    = sender_email
    msg["To"]      = ", ".join(receivers)
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        _log("[send_report] HTML 報告已成功寄出。")
        masked = "、".join(_mask_email(r) for r in receivers)
        _log(f"   收件者：{masked}（若沒看到信，請查垃圾郵件匣）")
    except Exception as e:
        _log(f"[send_report] 寄信錯誤: {e}")


if __name__ == "__main__":
    send_email()
