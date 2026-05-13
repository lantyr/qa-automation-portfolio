"""
Inject a collapsible date-trend table into allure-report/complete.html.
The table is fixed at the top of the page so it's always visible.

Run AFTER allure-combine and BEFORE archiving Report_*.html.
"""
import json
import os
import re

base          = os.path.dirname(os.path.abspath(__file__))
trend_json    = os.path.join(base, "allure-report", "history", "history-trend.json")
complete_html = os.path.join(base, "allure-report", "complete.html")

_MARKER = "<!-- custom-trend-injected -->"


def _build_banner(entries: list[dict]) -> str:
    dated = [e for e in entries if e.get("reportName")]
    rows = ""
    for e in dated:
        data    = e.get("data", {})
        name    = e.get("reportName", "")
        passed  = data.get("passed", 0)
        failed  = data.get("failed", 0) + data.get("broken", 0)
        skipped = data.get("skipped", 0)
        total   = data.get("total", 0)
        rate    = round(passed / total * 100, 1) if total else 0.0
        color   = "#2e7d32" if rate >= 90 else ("#f57f17" if rate >= 70 else "#c62828")
        rows += (
            f'<tr>'
            f'<td style="padding:5px 12px;border-bottom:1px solid #eee;white-space:nowrap;">{name}</td>'
            f'<td style="padding:5px 12px;border-bottom:1px solid #eee;text-align:center;">{total}</td>'
            f'<td style="padding:5px 12px;border-bottom:1px solid #eee;text-align:center;color:#2e7d32;">✅ {passed}</td>'
            f'<td style="padding:5px 12px;border-bottom:1px solid #eee;text-align:center;color:#c62828;">❌ {failed}</td>'
            f'<td style="padding:5px 12px;border-bottom:1px solid #eee;text-align:center;color:#f57f17;">⚠️ {skipped}</td>'
            f'<td style="padding:5px 12px;border-bottom:1px solid #eee;text-align:center;'
            f'font-weight:bold;color:{color};">{rate:.1f}%</td>'
            f'</tr>\n'
        )

    toggle_js = (
        "var b=document.getElementById('ctrb');"
        "var a=document.getElementById('ctra');"
        "if(b.style.display==='none'){b.style.display='block';a.textContent='▲';}"
        "else{b.style.display='none';a.textContent='▼';}"
    )

    return f"""{_MARKER}
<div id="custom-trend" style="position:fixed;top:0;left:0;right:0;z-index:99999;
     background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.25);
     font-family:Arial,'Microsoft JhengHei',sans-serif;font-size:13px;">
  <div style="padding:6px 16px;background:#1565c0;color:#fff;
              display:flex;justify-content:space-between;align-items:center;
              cursor:pointer;" onclick="{toggle_js}">
    <span style="font-weight:bold;font-size:14px;">📈 歷史趨勢（最近 {len(dated)} 次）</span>
    <span id="ctra" style="font-size:12px;">▲</span>
  </div>
  <div id="ctrb" style="overflow-y:auto;max-height:45vh;">
    <table style="width:100%;border-collapse:collapse;">
      <tr style="background:#f5f5f5;">
        <th style="padding:6px 12px;text-align:left;border-bottom:2px solid #ddd;position:sticky;top:0;background:#f5f5f5;">執行時間</th>
        <th style="padding:6px 12px;text-align:center;border-bottom:2px solid #ddd;position:sticky;top:0;background:#f5f5f5;">總數</th>
        <th style="padding:6px 12px;text-align:center;border-bottom:2px solid #ddd;position:sticky;top:0;background:#f5f5f5;">通過</th>
        <th style="padding:6px 12px;text-align:center;border-bottom:2px solid #ddd;position:sticky;top:0;background:#f5f5f5;">失敗</th>
        <th style="padding:6px 12px;text-align:center;border-bottom:2px solid #ddd;position:sticky;top:0;background:#f5f5f5;">跳過</th>
        <th style="padding:6px 12px;text-align:center;border-bottom:2px solid #ddd;position:sticky;top:0;background:#f5f5f5;">成功率</th>
      </tr>
      {rows}
    </table>
  </div>
</div>
<style>
  #custom-trend + * {{ margin-top: 80px !important; }}
  body > div:first-of-type {{ padding-top: 80px !important; }}
</style>
"""


def main() -> None:
    if not os.path.isfile(trend_json):
        print("[inject_trend] history-trend.json 不存在，跳過")
        return
    if not os.path.isfile(complete_html):
        print("[inject_trend] complete.html 不存在，跳過")
        return

    with open(trend_json, "r", encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    print(f"[inject_trend] 讀取 complete.html（可能需要幾秒）...")
    with open(complete_html, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    if _MARKER in html:
        # 已注入過 → 先移除舊的再重注入（保持最新趨勢資料）
        html = re.sub(
            r"<!-- custom-trend-injected -->.*?</style>\s*",
            "",
            html,
            flags=re.DOTALL,
        )
        print("[inject_trend] 移除舊版趨勢表，重新注入...")

    banner = _build_banner(entries)

    # 注入在 <body> 開始標籤之後
    html = re.sub(r"(<body[^>]*>)", r"\1" + banner, html, count=1)

    # Patch Trend chart X-axis: use reportName (date) instead of #buildOrder
    _OLD_LABEL = 'name:t.buildOrder?"#".concat(t.buildOrder):""'
    _NEW_LABEL = 'name:t.reportName||(t.buildOrder?"#".concat(t.buildOrder):"")'
    if _OLD_LABEL in html:
        html = html.replace(_OLD_LABEL, _NEW_LABEL, 1)
        print("[inject_trend] Trend X 軸已改為顯示日期")
    else:
        print("[inject_trend] WARNING: Trend X 軸 pattern 未找到（可能已 patch 或 Allure 版本不同）")

    print(f"[inject_trend] 寫回 complete.html...")
    with open(complete_html, "w", encoding="utf-8") as f:
        f.write(html)

    dated_count = sum(1 for e in entries if e.get("reportName"))
    print(f"[inject_trend] 完成，趨勢表含 {dated_count} 筆日期紀錄")


if __name__ == "__main__":
    main()
