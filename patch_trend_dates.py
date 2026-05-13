"""
Patch allure-report/history/history-trend.json with reportName = date string
so the Allure Trend chart shows actual dates on its X-axis.

Run AFTER `allure generate` and BEFORE `allure-combine`.
"""
import json
import glob
import os
import sys
from datetime import datetime

base        = os.path.dirname(os.path.abspath(__file__))
trend_json  = os.path.join(base, "allure-report", "history", "history-trend.json")
trend_log   = os.path.join(base, "HistoryReports", "trend_log.json")
results_dir = os.path.join(base, "allure-results")


def _current_run_date() -> str:
    min_ts: int | None = None
    for jf in glob.glob(os.path.join(results_dir, "*-result.json")):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                d = json.load(f)
            s = d.get("start")
            if s and (min_ts is None or s < min_ts):
                min_ts = s
        except Exception:
            continue
    if min_ts:
        return datetime.fromtimestamp(min_ts / 1000).strftime("%Y-%m-%d %H:%M")
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def main() -> None:
    if not os.path.isfile(trend_json):
        print("[patch_trend] history-trend.json 不存在，跳過")
        return

    with open(trend_json, "r", encoding="utf-8") as f:
        trend: list[dict] = json.load(f)

    if not trend:
        print("[patch_trend] history-trend.json 為空，跳過")
        return

    # 讀取歷史日期（最舊→最新排列）
    history_dates: list[str] = []
    if os.path.isfile(trend_log):
        try:
            with open(trend_log, "r", encoding="utf-8") as f:
                log: list[dict] = json.load(f)
            history_dates = [e.get("date", "") for e in log]
        except Exception:
            pass

    # trend[0] = 本次執行（最新），trend[1] = 上一次，依此類推（新→舊）
    current_date = _current_run_date()

    for i, entry in enumerate(trend):
        if i == 0:
            date_label = current_date
        elif i <= len(history_dates):
            # history_dates[-i] = 倒數第 i 筆（即第 i 次舊的執行）
            date_label = history_dates[-i]
        else:
            date_label = ""

        entry["reportName"] = date_label
        entry["buildOrder"] = len(trend) - i
        entry.setdefault("reportUrl", "#")

    with open(trend_json, "w", encoding="utf-8") as f:
        json.dump(trend, f, ensure_ascii=False, indent=2)

    print(f"[patch_trend] 已更新 {len(trend)} 筆，最新：{trend[0].get('reportName')}")


if __name__ == "__main__":
    main()
