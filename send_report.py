import smtplib
import os
import sys
import json
import glob
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv

# 讀取 .env 保險箱
load_dotenv()

# 排程 / cmd 預設 cp950 時，print(emoji) 會 UnicodeEncodeError；強制 UTF-8 或略過失敗
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError, AttributeError, TypeError):
            pass


def _log(msg: str) -> None:
    """Console log：避免 cp950 主控台無法輸出部分 Unicode（如 emoji）。"""
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(msg.encode(enc, errors="replace").decode(enc, errors="replace"))

# 固定一併收件（與 REPORT_RECEIVER_EMAIL 合併、去重）
_EXTRA_REPORT_RECEIVERS = ()


def _parse_receiver_list(raw: str) -> list[str]:
    out: list[str] = []
    for part in raw.replace(";", ",").split(","):
        addr = part.strip()
        if addr:
            out.append(addr)
    return out

def _is_credentials_skip(message: str) -> bool:
    """帳密未設定的 SKIP → 不顯示在報告、不計入統計。"""
    return "BEANFUN_" in message and ("缺少" in message or "請設定" in message)


def get_detailed_report(results_dir):
    """讀取 Allure JSON 並生成詳細的步驟清單"""
    all_reports = ""
    summary_data = {"total": 0, "passed": 0, "failed": 0, "locked": 0}

    json_files = glob.glob(os.path.join(results_dir, "*-result.json"))
    if not json_files:
        return "⚠️ 找不到任何測試結果，請確認 pytest 是否執行成功。", summary_data, 0

    features = {}
    _dedup = {}
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                feature_name = "未分類功能測試"
                for label in data.get('labels', []):
                    if label['name'] == 'feature':
                        feature_name = label['value']

                full_name = data.get("fullName") or data.get("name", "")
                dedup_key = (feature_name, full_name)
                stop_ts = data.get("stop", 0)
                if dedup_key in _dedup:
                    if stop_ts <= _dedup[dedup_key].get("stop", 0):
                        continue
                _dedup[dedup_key] = data
        except Exception:
            continue

    for (feature_name, _), data in _dedup.items():
        if feature_name not in features:
            features[feature_name] = []
        features[feature_name].append(data)

    feature_title_map = {
        "PC版官網登入頁": "一、基礎頁面與防呆驗證",
        "會員登入功能": "二、會員登入功能 (自動化測試用例結果)",
    }
    test_title_map = {
        "驗證：EMAIL登入純點帳進行登入測試 (全自動)": "驗證：EMAIL登入純點帳",
        "驗證：已開通整合點帳進行登入測試 (全自動)": "驗證：已開通整合點帳",
        "驗證：「舊 H5 需手動選取帳號」登入測試 (全自動)": "驗證：未開通整合點帳",
    }
    feature_order = [
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
    ordered_features = [f for f in feature_order if f in features] + [f for f in features if f not in feature_order]

    for feature in ordered_features:
        tests = sorted(features[feature], key=lambda t: t.get("name", ""))
        section_title = feature_title_map.get(feature, f"以下為 {feature} 的自動化測試用例結果")
        section_lines = ""
        t_idx = 0

        for test in tests:
            status = test.get('status', '')
            skip_message = test.get('statusDetails', {}).get('message', '')

            # 帳密未設定 → 完全不顯示、不計入
            if status == 'skipped' and _is_credentials_skip(skip_message):
                continue

            t_idx += 1
            summary_data["total"] += 1
            raw_test_name = test.get("name", "").strip()
            test_name = test_title_map.get(raw_test_name, raw_test_name)

            if status == 'passed':
                summary_data["passed"] += 1
                section_lines += f"{t_idx}. {test_name}\n\n"
                for s_idx, step in enumerate(test.get('steps', []), 1):
                    step_status = "OK" if step['status'] == 'passed' else "Failed"
                    step_name = step.get("name", "").strip()
                    step_name = re.sub(r"^步驟\s*\d+\s*:\s*", "", step_name)
                    step_name = re.sub(r"^\d+\.\s*", "", step_name)
                    section_lines += f"\t步驟 {s_idx}: {step_name} [{step_status}]\n\n"

            elif status == 'skipped':
                # 被鎖定（CAPTCHA、429、簡訊上限等）
                summary_data["locked"] += 1
                section_lines += f"{t_idx}. 🔒 {test_name}\n"
                reason = skip_message.strip().split("\n")[0] if skip_message else "環境限制"
                section_lines += f"\t原因：{reason}\n\n"

            else:
                # failed / broken
                summary_data["failed"] += 1
                section_lines += f"{t_idx}. {test_name}\n\n"
                for s_idx, step in enumerate(test.get('steps', []), 1):
                    step_status = "OK" if step['status'] == 'passed' else "Failed"
                    step_name = step.get("name", "").strip()
                    step_name = re.sub(r"^步驟\s*\d+\s*:\s*", "", step_name)
                    step_name = re.sub(r"^\d+\.\s*", "", step_name)
                    section_lines += f"\t步驟 {s_idx}: {step_name} [{step_status}]\n\n"

        if section_lines:
            all_reports += f"{section_title}\n{section_lines}\n"

    success_rate = (summary_data["passed"] / summary_data["total"] * 100) if summary_data["total"] > 0 else 0
    return all_reports, summary_data, success_rate


def _pick_local_report_html(base_dir: str) -> tuple[str, bool]:
    """優先 complete.html（allure-combine），否則 index.html（僅 allure generate）。回傳 (路徑, 檔案是否存在)。"""
    rd = os.path.join(base_dir, "allure-report")
    complete = os.path.join(rd, "complete.html")
    index_html = os.path.join(rd, "index.html")
    if os.path.isfile(complete):
        return complete, True
    if os.path.isfile(index_html):
        return index_html, True
    return complete, False


def _mask_email(addr: str) -> str:
    if not addr or "@" not in addr:
        return "(無效或未設定)"
    local, domain = addr.strip().split("@", 1)
    if len(local) <= 1:
        masked = "*" * min(3, max(1, len(local)))
    else:
        masked = local[0] + "***" + local[-1]
    return f"{masked}@{domain}"


def send_email():
    # 🟢 帳號設定：從保險箱 (.env) 拿密碼
    sender_email = (os.getenv("REPORT_SENDER_EMAIL") or "").strip()
    sender_password = (os.getenv("REPORT_SENDER_PWD") or "").strip()
    receiver_raw = (os.getenv("REPORT_RECEIVER_EMAIL") or "").strip()
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

    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(base_dir, "allure-results")
    report_html_path, report_file_ok = _pick_local_report_html(base_dir)
    report_missing_note = ""
    if not report_file_ok:
        report_missing_note = (
            "\n⚠️ 目前找不到 allure 網頁報告檔。"
            "請勿只執行 pytest：須再執行 run_tests.bat 的步驟 2～3（allure generate、allure-combine），"
            "並確認已安裝 Java（JDK）與 allure-commandline；單檔完整報告檔名為 complete.html。\n"
        )
    
    _log("[send_report] 正在生成詳細摘要報告...")
    detailed_text, summary, success_rate = get_detailed_report(results_path)

    status_icon = "✅" if summary["failed"] == 0 and summary["locked"] == 0 else "❌"
    subject = f"{status_icon} 官網自動化測試摘要 - 成功率: {success_rate:.0f}%"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(receivers)
    msg["Subject"] = Header(subject, "utf-8")

    # 🟢 移除了附件打包，改成直接提示本地檔案路徑
    body = f"""
您好，今日自動化測試已執行完畢，報告摘要如下：

{detailed_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 數據統計中心：
✅ 通過數量：{summary['passed']}
❌ 失敗數量：{summary['failed']}
🔒 被鎖定數量：{summary['locked']}
📈 總測試數：{summary['total']}
🏆 最終成功率：{success_rate:.1f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 【溫馨提示】
因為本次測試包含了大量的高清截圖，報告檔案超過了 Gmail 的 25MB 限制。
若要查看詳細截圖與互動報表，請直接在您的測試電腦上使用 Chrome 開啟以下檔案（建議優先使用 complete.html）：
📁 {report_html_path}
{report_missing_note}
自動化機器人 敬上
    """
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
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