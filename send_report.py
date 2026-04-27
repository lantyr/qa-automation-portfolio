import smtplib
import os
import sys
import json
import glob
import re
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

_DIV  = "━" * 26   # ━━━━━━━━━━━━━━━━━━━━━━━━━━
_DIV2 = "━" * 30   # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
    """嘗試從 Windows 登錄檔取得 Chrome 版本號。"""
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
    """從 allure-results JSON 取得最早 start 與最晚 stop（毫秒時間戳）。"""
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
    """
    優先取 HistoryReports 內最新的日期快照（Report_YYYYMMDD_HHMMSS.html）。
    這樣每封信的路徑都指向當次執行的固定檔案，事後點開不會看到其他日期的資料。
    若 HistoryReports 尚無檔案，則退而使用 allure-report/complete.html 或 index.html。
    """
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
    """
    讀取 allure-results，回傳：
      features      = { feature_name: [test_data, ...] }
      summary_data  = { total, passed, failed, locked }
      success_rate  = float
    """
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
    """'TC-XX-XXX：描述' → 'TC-XX-XXX: 描述'"""
    return raw.replace("：", ": ")


def _format_detailed_section(features: dict) -> str:
    """依大分類 → 功能 → 測試案例 → 步驟 格式化詳細結果。"""
    ordered = [f for f in _FEATURE_ORDER if f in features] + \
              [f for f in features if f not in _FEATURE_ORDER]

    # 先依大分類分組
    categories: dict[str, list[str]] = {}
    for feat in ordered:
        cat = _FEATURE_CATEGORY.get(feat, "📋 其他測試")
        categories.setdefault(cat, []).append(feat)

    cat_order = _CATEGORY_ORDER + [c for c in categories if c not in _CATEGORY_ORDER]

    lines = ""
    for cat in cat_order:
        if cat not in categories:
            continue
        lines += f"{_DIV2}\n{cat}\n{_DIV2}\n\n"

        for feat in categories[cat]:
            lines += f"【{feat}】\n"
            tests = sorted(features[feat], key=lambda t: t.get("name", ""))

            for test in tests:
                status       = test.get("status", "")
                skip_message = test.get("statusDetails", {}).get("message", "")
                raw_name     = test.get("name", "").strip()
                test_name    = _format_test_name(raw_name)

                if status == "passed":
                    lines += f"  {test_name} [PASS]\n"
                    for s_idx, step in enumerate(test.get("steps", []), 1):
                        sname = step.get("name", "").strip()
                        sname = re.sub(r"^步驟\s*\d+\s*:\s*", "", sname)
                        sname = re.sub(r"^\d+\.\s*", "", sname)
                        lines += f"    步驟 {s_idx}: {sname} [PASS]\n"
                    lines += "\n"

                elif status == "skipped":
                    reason = skip_message.strip().split("\n")[0] if skip_message else "環境限制"
                    lines += f"  🔒 {test_name} [SKIP]\n"
                    lines += f"    原因：{reason}\n\n"

                else:
                    lines += f"  {test_name} [FAIL]\n"
                    for s_idx, step in enumerate(test.get("steps", []), 1):
                        s_status = "PASS" if step["status"] == "passed" else "FAIL"
                        sname = step.get("name", "").strip()
                        sname = re.sub(r"^步驟\s*\d+\s*:\s*", "", sname)
                        sname = re.sub(r"^\d+\.\s*", "", sname)
                        lines += f"    步驟 {s_idx}: {sname} [{s_status}]\n"
                    lines += "\n"

            lines += "\n"

    return lines.rstrip()


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

    # ── 詳細結果 ──────────────────────────────────────────────
    detailed_text = _format_detailed_section(features) if features else "⚠️ 找不到任何測試結果。"

    # ── 本地報告路徑 ──────────────────────────────────────────
    report_note = (
        f"📁 {report_html_path}"
        if report_file_ok
        else f"⚠️ 找不到報告檔，預期路徑：{report_html_path}"
    )

    # ── 郵件主旨 ──────────────────────────────────────────────
    status_icon = "✅" if summary["failed"] == 0 and summary["locked"] == 0 else "❌"
    subject = f"{status_icon} 官網自動化測試摘要 - 成功率: {success_rate:.0f}%"

    body = f"""您好，今日自動化測試已執行完畢，報告摘要如下：

{_DIV}
📋 測試環境資訊
{_DIV}
測試執行時間: {start_str} ~ {end_str}
測試執行耗時: {elapsed:.2f} 秒
測試裝置: {os_name} + Chrome (Headless)
Chrome 版本: {chrome_ver}
網路環境: {hostname} / {ip}
測試框架: pytest + Selenium WebDriver
報告工具: Allure
測試狀態: {status_text}

{_DIV}
📊 測試統計
{_DIV}
總測試數: {summary['total']}
通過測試: {summary['passed']}
失敗測試: {summary['failed']}
異常/跳過: {summary['locked']}
成功率: {success_rate:.1f}%

{_DIV}
📝 詳細測試結果
{_DIV}
{detailed_text}

{report_note}

自動化機器人 敬上"""

    msg = MIMEMultipart()
    msg["From"]    = sender_email
    msg["To"]      = ", ".join(receivers)
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        _log("[send_report] 摘要報告已成功寄出。")
        masked = "、".join(_mask_email(r) for r in receivers)
        _log(f"   收件者：{masked}（若沒看到信，請查垃圾郵件匣）")
    except Exception as e:
        _log(f"[send_report] 寄信錯誤: {e}")


if __name__ == "__main__":
    send_email()