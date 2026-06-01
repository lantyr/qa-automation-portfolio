"""
Cross-run historical trend table builder.

Maintains a rolling trend.json in HistoryReports/ that records each run's
pass/fail/skip counts. inject_into_html() inserts the rendered table into
the HTML email before the per-test results table.

Usage (called by send_report.py automatically):
    from utils.report.inject_trend_table import append_run, build_trend_html, inject_into_html
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORY_DIR = ROOT / "HistoryReports"
TREND_JSON = HISTORY_DIR / "trend.json"


def load_trend() -> list[dict]:
    if not TREND_JSON.exists():
        return []
    try:
        return json.loads(TREND_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_trend(data: list[dict]) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    TREND_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_run(summary: dict) -> None:
    """Append current run summary to rolling trend (capped at 30 entries)."""
    trend = load_trend()
    trend.append(summary)
    if len(trend) > 30:
        trend = trend[-30:]
    save_trend(trend)


def build_trend_html(trend: list[dict]) -> str:
    if not trend:
        return ""
    rows = ""
    for entry in reversed(trend[-10:]):
        rate = entry.get("pass_rate", 0)
        color = "#28a745" if rate >= 80 else "#ffc107" if rate >= 60 else "#dc3545"
        rows += (
            f"<tr>"
            f"<td style='padding:6px 8px;border:1px solid #dee2e6'>{entry.get('date', '—')}</td>"
            f"<td style='padding:6px 8px;border:1px solid #dee2e6;color:{color};font-weight:bold'>{rate}%</td>"
            f"<td style='padding:6px 8px;border:1px solid #dee2e6;color:#28a745'>{entry.get('passed', 0)}</td>"
            f"<td style='padding:6px 8px;border:1px solid #dee2e6;color:#dc3545'>{entry.get('failed', 0)}</td>"
            f"<td style='padding:6px 8px;border:1px solid #dee2e6;color:#6c757d'>{entry.get('skipped', 0)}</td>"
            f"<td style='padding:6px 8px;border:1px solid #dee2e6'>{entry.get('total', 0)}</td>"
            f"</tr>"
        )
    header_style = "padding:8px;border:1px solid #dee2e6;text-align:left"
    return (
        "<h3 style='margin-top:24px'>歷史趨勢（最近 10 次）</h3>"
        "<table style='border-collapse:collapse;width:100%;margin-bottom:20px'>"
        "<thead><tr style='background:#343a40;color:#fff'>"
        f"<th style='{header_style}'>日期</th>"
        f"<th style='{header_style}'>通過率</th>"
        f"<th style='{header_style}'>通過</th>"
        f"<th style='{header_style}'>失敗</th>"
        f"<th style='{header_style}'>跳過</th>"
        f"<th style='{header_style}'>總計</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
    )


def inject_into_html(html: str, trend_html: str) -> str:
    """Insert trend table immediately before the first <table> in the HTML."""
    if not trend_html:
        return html
    marker = "<table"
    idx = html.find(marker)
    if idx == -1:
        return html + trend_html
    return html[:idx] + trend_html + html[idx:]
