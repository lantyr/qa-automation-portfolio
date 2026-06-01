# QA Automation Portfolio

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white" alt="Selenium">
  <img src="https://img.shields.io/badge/Playwright-1.40+-2EAD33?logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/pytest-8.x-0A9EDC?logo=pytest&logoColor=white" alt="pytest">
  <img src="https://img.shields.io/badge/Allure-Report-FF6B35" alt="Allure">
  <img src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white" alt="CI">
</p>

<p align="center">
  以公開 Demo 站為目標的 <strong>API + UI 自動化測試框架</strong>，同時涵蓋 <strong>Mobile 模擬版（Selenium）</strong> 與 <strong>PC 桌面版（Playwright）</strong>，採嚴格 Page Object Model 架構，整合 Allure 報告、Email 通知、Slack 推播與歷史趨勢追蹤。
</p>

---

## 目錄

- [技術棧](#技術棧)
- [測試範圍](#測試範圍)
- [架構設計](#架構設計)
- [核心設計決策](#核心設計決策)
- [報告系統](#報告系統)
- [排程與通知](#排程與通知)
- [環境設定](#環境設定)
- [執行測試](#執行測試)
- [開發規範](#開發規範)

---

## 技術棧

| 類別 | 工具 |
|------|------|
| **語言** | Python 3.12+ |
| **UI 自動化（Mobile）** | Selenium WebDriver + Chrome Mobile Emulation（模擬 iPhone） |
| **UI 自動化（PC）** | Playwright（Chromium，內建自動等待） |
| **API 測試** | requests（從登入後的瀏覽器抽取 cookies 建立共用 session） |
| **測試框架** | pytest + pytest-xdist（平行執行）|
| **架構模式** | Page Object Model（POM） |
| **報告系統** | Allure Report + 自製 HTML Email 報告 + 歷史趨勢表 |
| **通知整合** | Slack Webhook、Gmail SMTP |
| **雲端歸檔** | Google Drive API |
| **環境管理** | python-dotenv |
| **排程** | Windows Task Scheduler（`.ps1` 腳本驅動） |

---

## 測試範圍

本 portfolio 以兩個不同維度的公開 Demo 站為目標，模擬真實產品的測試分層策略：

### 📱 Mobile 版 — [saucedemo.com](https://www.saucedemo.com)（Selenium + iPhone Emulation）

| Test ID | 類別 | 測試項目 |
|---------|------|----------|
| M-LOG-001 | Login | 標準帳號登入 → 商品頁 |
| M-LOG-002 | Login | 鎖定帳號登入 → 錯誤訊息驗證 |
| M-LOG-003 | Login | 錯誤密碼 → 通用錯誤（不洩漏帳號存在性） |
| M-INV-001 | Inventory | 行動版商品頁列出正確數量 |
| M-INV-002 | Inventory | 排序「價格低→高」驗證遞增 |
| M-CHK-001 | Checkout | 加入購物車後 badge 數字更新 |
| M-CHK-002 | Checkout | 完整結帳流程（登入 → 加購 → 填資料 → 確認） |
| M-NAV-001 | Navigation | 行動版選單開關、導覽項目驗證 |

### 🖥️ PC 版 — [reqres.in](https://reqres.in)（Playwright + API）

| Test ID | 類別 | 測試項目 |
|---------|------|----------|
| USR-001 | Users | 列出使用者（分頁）+ JSON Schema 驗證 |
| USR-002 | Users | 取得單一使用者 |
| USR-003 | Users | 取得不存在使用者 → 404 |
| USR-004 | Users | 建立使用者 → 201 + id + createdAt |
| AUT-001 | Auth | 使用者註冊成功 → id + token |
| AUT-002 | Auth | 註冊缺少密碼 → 400 |
| AUT-003 | Auth | 使用者登入成功 → token |
| AUT-004 | Auth | 登入未知使用者 → 400 |
| RBS-001 | Robustness | 回應時間 < 3 秒 |
| RBS-002 | Robustness | Content-Type 驗證 |
| RBS-003 | Robustness | GET 冪等性驗證 |
| RBS-004 | Robustness | 非法 id 優雅降級（不得 5xx）— parametrize 3 種 |

---

## 架構設計

```
qa-automation-portfolio/
├── mobile_pack/                  # 📱 Mobile 模組（Selenium）
│   ├── pages/                    # POM：行動版頁面物件
│   │   ├── base_page.py          # 共用等待 / 安全點擊封裝
│   │   ├── login_page.py
│   │   ├── inventory_page.py
│   │   └── checkout_page.py
│   ├── tests/
│   │   ├── api/                  # API 層測試（requests）
│   │   └── ui/                   # UI 層測試（Selenium mobile emulation）
│   └── conftest.py               # mobile_driver fixture、自動失敗截圖
│
├── web_pack/                     # 🖥️ PC 版模組（Playwright）
│   ├── pages/                    # POM：桌面版頁面物件
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   ├── inventory_page.py
│   │   └── checkout_page.py
│   ├── tests/
│   │   ├── api/                  # API 層測試（reqres.in）
│   │   └── ui/                   # UI 層測試（Playwright Chromium）
│   └── conftest.py               # playwright fixture、自動截圖 hook
│
├── utils/                        # 共用工具
│   ├── api_session.py            # 從瀏覽器 cookies 建立 requests session
│   └── report/
│       ├── send_report.py        # HTML Email 報告產生與寄送
│       ├── inject_trend_table.py # 跨執行歷史趨勢表注入
│       └── patch_trend_dates.py  # Allure 趨勢圖日期修補
│
├── config/                       # 環境設定
│   ├── settings.py               # frozen dataclass，唯一設定來源
│   └── credentials.py            # .env 憑證讀取封裝
│
├── data/                         # 外部測試資料（JSON）
├── categories.json               # Allure 分類規則（環境限制 vs 真實 Bug）
├── run_tests_scheduled.ps1       # 排程腳本（測試 → Allure → 報告 → 通知）
├── .github/workflows/ci.yml      # GitHub Actions CI
├── pytest.ini
├── requirements.txt
└── .env.example                  # 環境變數樣板（無任何密碼）
```

---

## 核心設計決策

| 決策 | 說明 |
|------|------|
| **雙引擎 UI** | Mobile 用 Selenium Chrome Mobile Emulation 模擬真實手機行為；PC 用 Playwright 利用內建自動等待降低 flaky 率 |
| **API ↔ UI 交叉驗證** | 登入後從瀏覽器抽取 cookies 建立共用 session，讓 API 測試與 UI 狀態保持一致 |
| **嚴格 POM** | 所有 Selector 只存在於 `pages/`，測試檔案零 locator，降低維護成本 |
| **動態等待** | 禁止 `sleep()` 固定等待，一律使用元件狀態導向的動態等待 |
| **Allure 三層分類** | `categories.json` 區隔「環境限制造成的 skip」與「真實 Bug」，降低誤報率 |
| **資料外部化** | 帳號、輸入值從 `data/` JSON 載入，機密透過 `.env` 注入，禁止硬編碼 |
| **狀態隔離** | 每個測試 function scope 獨立 driver，支援 `-n auto` 平行執行，測試間互不污染 |

---

## 報告系統

### Allure Report
- UI 測試失敗或 skip 時，自動截圖並附加至 Allure 報告
- `categories.json` 將「環境限制 skip」與「真實 Bug」分層，面試官或主管可快速 triage
- 每次執行自動合併歷史趨勢，支援跨執行次的 Pass Rate 變化追蹤

### HTML Email 報告（`send_report.py`）
- 手風琴式結果展開、內嵌失敗截圖（CID inline）
- 跨執行次**歷史趨勢表**（`inject_trend_table.py`）
- 測試環境資訊、執行時間、各功能通過率一覽
- 完整 Allure 報告自動上傳 Google Drive，信件附上分享連結

### Slack 通知
- 執行結束後自動推送摘要至指定頻道（成功率、失敗數、Drive 連結）

---

## 排程與通知

`run_tests_scheduled.ps1` 一鍵完成完整流程：

```
Mobile UI 測試 → PC UI 測試 → API 測試
    → 合併 Allure 歷史結果
    → 產生 Allure HTML 報告
    → 封存至 HistoryReports/
    → 寄送 HTML Email 報告
    → 上傳 Google Drive
    → 推送 Slack 通知
```

可掛 Windows 工作排程器定時執行（如每日 06:00）。

---

## 環境設定

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
playwright install chromium --with-deps
```

### 2. 設定環境變數

```bash
cp .env.example .env
```

`.env.example` 主要變數（皆為公開 Demo 帳號，可直接執行）：

```env
# UI 測試目標
SAUCE_BASE_URL=https://www.saucedemo.com
SAUCE_USER_STANDARD=standard_user
SAUCE_PASSWORD=secret_sauce

# API 測試目標
REQRES_BASE_URL=https://reqres.in/api

# 瀏覽器模式
BROWSER_MODE=headless

# 報告通知（選填）
REPORT_SENDER_EMAIL=
REPORT_SENDER_PWD=
REPORT_RECEIVER_EMAIL=
SLACK_WEBHOOK_URL=
GDRIVE_FOLDER_ID=
```

> 未填入通知相關變數時，Email / Slack / Drive 功能會自動跳過，不影響測試執行。

### 3. Google Drive 授權（選填）

```bash
python utils/report/gdrive_auth.py
```

---

## 執行測試

```bash
# 執行全部測試
pytest

# 只跑 Mobile UI
pytest mobile_pack/tests/ui -m ui

# 只跑 PC API
pytest web_pack/tests/api -m api

# 只跑 smoke（核心路徑）
pytest -m smoke

# 只跑負向測試
pytest -m negative

# 平行執行
pytest -n auto

# 產生 Allure 報告
pytest --alluredir=allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report

# 預覽 Email 報告（不實際寄送）
python utils/report/send_report.py --preview
```

---

## 支援的測試 Markers

| Marker | 用途 |
|--------|------|
| `api` | 所有 API 測試 |
| `ui` | 所有 UI 測試（需要瀏覽器） |
| `mobile` | Mobile 模擬版測試（Selenium） |
| `web` | PC 桌面版測試（Playwright） |
| `smoke` | 核心路徑，每次 commit 必須通過 |
| `negative` | 負向 / 錯誤路徑測試 |

---

## 開發規範

- 禁止在測試檔直接寫 Selector — 必須透過 POM
- 禁止使用 `sleep()` 固定等待 — Mobile 用動態等待封裝，PC 用 Playwright 內建等待
- 禁止使用 JavaScript 注入繞過 UI 操作
- 禁止硬編碼帳號密碼 — 必須透過 `.env`
- 每個 Test Case 包含 Test ID、步驟、預期結果（寫在 docstring）
- Flaky test 必須根因處理，禁止用 retry 掩蓋
- 報告狀態判定等共用邏輯遵守 DRY，只寫一套

---

## License

MIT
