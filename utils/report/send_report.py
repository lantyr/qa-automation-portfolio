"""
HTML email report generator with inline screenshots, Google Drive upload, and Slack push.

Usage:
    python utils/report/send_report.py            # full run: upload + email + Slack
    python utils/report/send_report.py --preview  # write report-preview.html and open it
"""
from __future__ import annotations

import argparse
import base64
import json
import smtplib
import socket
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLURE_RESULTS = ROOT / "allure-results"
ALLURE_REPORT = ROOT / "allure-report"

sys.path.insert(0, str(ROOT))
from config.credentials import credentials  # noqa: E402
from utils.report.inject_trend_table import (  # noqa: E402
    append_run,
    build_trend_html,
    inject_into_html,
    load_trend,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_allure_results() -> list[dict]:
    results = []
    if not ALLURE_RESULTS.exists():
        return results
    for f in ALLURE_RESULTS.glob("*-result.json"):
        try:
            results.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return results


def _compute_summary(results: list[dict]) -> dict:
    counts: dict = {"passed": 0, "failed": 0, "broken": 0, "skipped": 0}
    for r in results:
        status = r.get("status", "unknown")
        if status in counts:
            counts[status] += 1
    counts["total"] = sum(v for k, v in counts.items() if k != "total")
    counts["pass_rate"] = (
        round(100 * counts["passed"] / counts["total"], 1) if counts["total"] else 0
    )
    counts["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return counts


def _screenshot_b64(result: dict) -> str | None:
    for att in result.get("attachments", []):
        if att.get("type") == "image/png":
            att_path = ALLURE_RESULTS / att["source"]
            if att_path.exists():
                return base64.b64encode(att_path.read_bytes()).decode()
    return None


# ---------------------------------------------------------------------------
# HTML builder
# ---------------------------------------------------------------------------

def _build_html(summary: dict, results: list[dict], drive_link: str = "") -> str:
    host = socket.gethostname()
    rate = summary["pass_rate"]
    rate_color = "#28a745" if rate >= 80 else "#ffc107" if rate >= 60 else "#dc3545"

    rows = ""
    for r in sorted(results, key=lambda x: (x.get("status", ""), x.get("name", ""))):
        status = r.get("status", "unknown").upper()
        name = r.get("name", "—")
        feature = next(
            (lbl["value"] for lbl in r.get("labels", []) if lbl.get("name") == "feature"),
            "—",
        )
        status_color = {
            "PASSED": "#28a745",
            "FAILED": "#dc3545",
            "BROKEN": "#e67e22",
            "SKIPPED": "#6c757d",
        }.get(status, "#333")

        img_html = ""
        if status in ("FAILED", "BROKEN"):
            b64 = _screenshot_b64(r)
            if b64:
                img_html = (
                    "<details><summary style='color:#0d6efd;cursor:pointer'>截圖</summary>"
                    f"<img src='data:image/png;base64,{b64}' style='max-width:600px;margin-top:8px'/>"
                    "</details>"
                )

        rows += (
            f"<tr>"
            f"<td style='color:{status_color};font-weight:bold;white-space:nowrap'>{status}</td>"
            f"<td>{feature}</td>"
            f"<td>{name}{img_html}</td>"
            f"</tr>"
        )

    drive_section = (
        f"<p>📁 完整 Allure 報告：<a href='{drive_link}'>{drive_link}</a></p>"
        if drive_link
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="utf-8">
<style>
  body{{font-family:Arial,sans-serif;font-size:14px;color:#333;max-width:900px;margin:auto}}
  .summary{{background:#f8f9fa;padding:16px;border-radius:6px;margin-bottom:16px}}
  .pass-rate{{font-size:32px;font-weight:bold;color:{rate_color}}}
  table{{border-collapse:collapse;width:100%}}
  th,td{{border:1px solid #dee2e6;padding:8px;text-align:left;vertical-align:top}}
  th{{background:#343a40;color:#fff}}
  tr:nth-child(even){{background:#f8f9fa}}
</style>
</head>
<body>
<h2>QA Automation Test Report</h2>
<div class="summary">
  <span class="pass-rate">{rate}%</span> 通過率 &nbsp;|&nbsp;
  Total: {summary['total']} &nbsp;|&nbsp;
  <span style="color:#28a745">✔ {summary['passed']}</span> &nbsp;|&nbsp;
  <span style="color:#dc3545">✘ {summary['failed']}</span> &nbsp;|&nbsp;
  <span style="color:#e67e22">⚠ {summary['broken']}</span> &nbsp;|&nbsp;
  <span style="color:#6c757d">⊘ {summary['skipped']}</span>
  <br><small>執行時間：{summary['date']} &nbsp;|&nbsp; 環境：{host}</small>
</div>
{drive_section}
<table>
  <thead><tr><th>狀態</th><th>功能模組</th><th>測試案例</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</body></html>"""


# ---------------------------------------------------------------------------
# Google Drive upload
# ---------------------------------------------------------------------------

def _upload_to_drive() -> str:
    folder_id = credentials.gdrive_folder_id
    if not folder_id or not ALLURE_REPORT.exists():
        return ""
    try:
        import tempfile
        import zipfile

        from google.oauth2.credentials import Credentials as GCreds
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        token_file = ROOT / "token.json"
        if not token_file.exists():
            print("[Drive] token.json not found — skipping upload")
            return ""

        creds = GCreds.from_authorized_user_file(str(token_file))
        service = build("drive", "v3", credentials=creds, cache_discovery=False)

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in ALLURE_REPORT.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(ALLURE_REPORT.parent))
            archive = tmp.name

        label = datetime.now().strftime("%Y%m%d-%H%M")
        meta = {
            "name": f"allure-report-{label}.zip",
            "parents": [folder_id],
            "mimeType": "application/zip",
        }
        media = MediaFileUpload(archive, mimetype="application/zip", resumable=True)
        result = service.files().create(body=meta, media_body=media, fields="id").execute()
        file_id = result.get("id", "")
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
        link = f"https://drive.google.com/file/d/{file_id}/view"
        print(f"[Drive] Uploaded → {link}")
        return link
    except Exception as exc:
        print(f"[Drive] Upload failed: {exc}")
        return ""


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def _send_email(html: str, summary: dict) -> None:
    sender = credentials.report_sender_email
    pwd = credentials.report_sender_pwd
    receiver = credentials.report_receiver_email
    if not all([sender, pwd, receiver]):
        print("[Email] Skipped — REPORT_SENDER_EMAIL / REPORT_SENDER_PWD / REPORT_RECEIVER_EMAIL not set.")
        return

    subject = (
        f"[QA Report] {summary['pass_rate']}% 通過率 "
        f"({summary['passed']}/{summary['total']}) — {summary['date']}"
    )
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, pwd)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"[Email] Sent to {receiver}")
    except Exception as exc:
        print(f"[Email] Failed: {exc}")


# ---------------------------------------------------------------------------
# Slack
# ---------------------------------------------------------------------------

def _send_slack(summary: dict, drive_link: str) -> None:
    url = credentials.slack_webhook_url
    if not url:
        print("[Slack] Skipped — SLACK_WEBHOOK_URL not set.")
        return
    try:
        import urllib.request

        rate = summary["pass_rate"]
        emoji = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
        text = (
            f"{emoji} *QA Report* — {summary['date']}\n"
            f"通過率：*{rate}%* "
            f"（通過 {summary['passed']} / 失敗 {summary['failed']} / "
            f"跳過 {summary['skipped']} / 共 {summary['total']}）"
        )
        if drive_link:
            text += f"\n📁 <{drive_link}|Allure 報告>"

        payload = json.dumps({"text": text}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        print("[Slack] Notification sent.")
    except Exception as exc:
        print(f"[Slack] Failed: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and send QA test report.")
    parser.add_argument("--preview", action="store_true", help="Write HTML to disk and open in browser.")
    args = parser.parse_args()

    results = _load_allure_results()
    summary = _compute_summary(results)

    drive_link = "" if args.preview else _upload_to_drive()
    html_body = _build_html(summary, results, drive_link)

    append_run(summary)
    trend_html = build_trend_html(load_trend())
    html_body = inject_into_html(html_body, trend_html)

    if args.preview:
        out = ROOT / "report-preview.html"
        out.write_text(html_body, encoding="utf-8")
        print(f"[Preview] Saved → {out}")
        import webbrowser
        webbrowser.open(str(out))
    else:
        _send_email(html_body, summary)
        _send_slack(summary, drive_link)


if __name__ == "__main__":
    main()
