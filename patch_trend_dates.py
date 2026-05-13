"""
Patch allure-report/history/history-trend.json with reportName = date string
so the Allure Trend chart shows actual dates on its X-axis.

Date source: HistoryReports/Report_YYYYMMDD_HHMMSS.html filenames (newest-first)
are positionally matched to history-trend entries (newest = index 0).

Also syncs HistoryReports/trend_log.json so the email trend table stays aligned.

Run AFTER `allure generate` and BEFORE `allure-combine`.
"""
import json
import glob
import os
import re
from datetime import datetime

base          = os.path.dirname(os.path.abspath(__file__))
trend_json    = os.path.join(base, "allure-report", "history", "history-trend.json")
trend_log     = os.path.join(base, "HistoryReports", "trend_log.json")
history_dir   = os.path.join(base, "HistoryReports")
results_dir   = os.path.join(base, "allure-results")


def _report_dates_newest_first() -> list[str]:
    """從 Report_*.html 檔名提取日期，最新在前。"""
    files = sorted(
        glob.glob(os.path.join(history_dir, "Report_*.html")),
        reverse=True,
    )
    dates = []
    for f in files:
        m = re.search(r"Report_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})", os.path.basename(f))
        if m:
            dates.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)} {m.group(4)}:{m.group(5)}")
    return dates


def _current_run_date() -> str:
    """從 allure-results JSON 取得本次執行的最早開始時間。"""
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


def _sync_trend_log(report_dates: list[str]) -> None:
    """用 Report_*.html 的日期清單補齊 trend_log.json 裡缺少日期的舊筆。
    只補日期欄位；pass/fail 等統計值若無法取得則留空，讓後續 send_report 覆蓋。
    """
    log: list[dict] = []
    if os.path.isfile(trend_log):
        try:
            with open(trend_log, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            log = []

    existing_dates = {e.get("date", "") for e in log}

    # report_dates 是新→舊，trend_log 是舊→新
    # 找出 trend_log 裡沒有的舊日期並補入（無統計數字，僅佔位）
    added = 0
    for date in reversed(report_dates):          # 舊→新走訪
        if date and date not in existing_dates:
            log.insert(0, {"date": date, "total": 0, "passed": 0,
                           "failed": 0, "locked": 0, "rate": 0.0})
            existing_dates.add(date)
            added += 1

    # 按日期排序（舊→新）後裁剪
    log.sort(key=lambda e: e.get("date", ""))
    log = log[-14:]

    try:
        with open(trend_log, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        if added:
            print(f"[patch_trend] trend_log.json 補入 {added} 筆舊日期")
    except Exception as e:
        print(f"[patch_trend] trend_log.json 寫入失敗：{e}")


def main() -> None:
    if not os.path.isfile(trend_json):
        print("[patch_trend] history-trend.json 不存在，跳過")
        return

    with open(trend_json, "r", encoding="utf-8") as f:
        trend: list[dict] = json.load(f)

    if not trend:
        print("[patch_trend] history-trend.json 為空，跳過")
        return

    # Report 檔名日期（新→舊），與 history-trend 索引順序一致
    report_dates = _report_dates_newest_first()

    # history-trend[0] = 本次執行（Report_*.html 尚未產生）
    # 所以 history-trend[0] 對應 allure-results 的實際執行時間
    # history-trend[1] ↔ report_dates[0]（上一個 Report）
    # history-trend[2] ↔ report_dates[1]
    # ...
    current_date = _current_run_date()

    for i, entry in enumerate(trend):
        if i == 0:
            date_label = current_date
        else:
            idx = i - 1     # report_dates[0] = 上一個 Report = history-trend[1]
            date_label = report_dates[idx] if idx < len(report_dates) else ""

        entry["reportName"] = date_label
        entry["buildOrder"] = len(trend) - i
        entry.setdefault("reportUrl", "#")

    with open(trend_json, "w", encoding="utf-8") as f:
        json.dump(trend, f, ensure_ascii=False, indent=2)

    print(f"[patch_trend] history-trend.json 已更新 {len(trend)} 筆")
    for i, e in enumerate(trend[:5]):
        print(f"  [{i}] {e.get('reportName','(空)')}  passed={e['data'].get('passed')} total={e['data'].get('total')}")
    if len(trend) > 5:
        print(f"  ... 共 {len(trend)} 筆")

    # 同步 trend_log.json（讓 email 趨勢與 Allure 一致）
    _sync_trend_log(report_dates)


if __name__ == "__main__":
    main()
