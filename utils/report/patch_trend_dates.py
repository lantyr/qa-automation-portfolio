"""
Patch Allure history trend timestamps to human-readable YYYY-MM-DD HH:MM format.

Allure stores trend build orders as epoch milliseconds. Some Allure versions
render these as raw integers in the timeline widget. Running this script after
`allure generate` converts them to readable strings for the report UI.

Usage:
    python utils/report/patch_trend_dates.py
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORY_TREND = ROOT / "allure-report" / "history" / "trend.json"


def patch() -> None:
    if not HISTORY_TREND.exists():
        print(f"[patch_trend_dates] {HISTORY_TREND} not found — skipping")
        return

    data = json.loads(HISTORY_TREND.read_text(encoding="utf-8"))
    changed = 0
    for entry in data:
        ts = entry.get("buildOrder")
        if isinstance(ts, int) and ts > 1_000_000_000_000:
            entry["buildOrder"] = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M")
            changed += 1

    HISTORY_TREND.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[patch_trend_dates] Patched {changed}/{len(data)} entries in {HISTORY_TREND}")


if __name__ == "__main__":
    patch()
