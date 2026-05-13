# GamaPass Automation Test Framework

> beanfun / GamaPass PC 網站 UI 自動化測試框架，採用 Page Object Model 架構，支援每日排程執行與自動化報告寄送。

---

## 專案概覽

本專案為 **beanfun GamaPass PC 官網**的完整自動化測試解決方案，涵蓋登入驗證、核心功能操作至報告產出的完整測試生命週期，由本人獨立設計與實作。

| 項目 | 內容 |
|---|---|
| 測試模組 | 13 個 |
| 測試案例 | 100+ TC |
| 測試框架 | pytest + Selenium |
| 報告系統 | Allure Report + Email 自動寄送 |
| 執行環境 | Windows 排程 / Docker |

---

## 技術棧

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.41+-green)
![pytest](https://img.shields.io/badge/pytest-9.0+-orange)
![Allure](https://img.shields.io/badge/Allure-2.15+-yellow)
![Docker](https://img.shields.io/badge/Docker-支援-blue)

- **UI 自動化**：Selenium WebDriver 4.x
- **測試框架**：pytest + allure-pytest
- **架構模式**：Page Object Model (POM)
- **環境管理**：python-dotenv
- **容器化**：Docker + docker-compose
- **報告系統**：Allure Report、HTML Email、Google Drive 備份

---

## 測試範圍

### 登入模組

| Test ID | 測試項目 |
|---|---|
| TC-LOGIN-PC-001 | 純點帳帳密登入 |
| TC-LOGIN-OID-001~005 | OpenID 登入（純點帳 / bf!帳 / GP帳 / GamaPass / 星帳）|
| TC-MIGRATE | 帳號遷移登入流程 |
| TC-NEGATIVE | 負向登入測試（錯誤帳密、邊界案例）|
| TC-API | API 層級 GamaPass 登入驗證 |

### PC 版功能模組

| Test ID 範圍 | 測試項目 |
|---|---|
| TC-PC-HOME | 首頁功能驗證、影片播放 |
| TC-PC-ACTION-BAR | 右側功能列操作 |
| SC-P-001~021 | 純點帳會員中心側欄（21 TC）|
| SC-S-001~022 | 星帳會員中心側欄（22 TC）|
| TC-PC-SP-001~017 | 儲值與購點彈窗（17 TC）|
| TC-PC-MC | 會員中心頁面驗證 |
| TC-PC-CS | 客服中心頁面驗證 |
| TC-PC-NAVBAR | 導覽列狀態驗證 |

---

## 架構設計

```
GamaPass-Automation/
├── pages/              # Page Object Model — UI 元件與頁面操作
│   ├── base_page.py    # 共用基底類別（動態等待、截圖、Alert 處理）
│   ├── home_page.py    # 首頁
│   ├── login_page.py   # 登入頁（多帳號類型）
│   ├── member_center_page.py
│   └── topup_popup_page.py
├── tests/              # 純測試邏輯，不含任何 locator
├── config/
│   └── credentials.py  # 帳號憑證管理（從 .env 讀取）
├── data/               # 測試資料（JSON）
├── allure-results/     # Allure 原始結果
├── HistoryReports/     # 歷史報告趨勢追蹤
├── send_report.py      # Email 報告自動寄送
├── inject_trend_table.py  # 跨次執行 pass rate 趨勢分析
├── conftest.py         # pytest hooks、driver fixture、自動截圖
└── docker-compose.yml
```

### 核心架構決策

- **嚴格 POM**：所有 XPath / CSS Selector 只存在於 `pages/`，測試檔案零 locator
- **資料驅動**：帳號、密碼、OTP 全部透過 `.env` 環境變數注入，禁止硬編碼
- **動態等待**：全面使用 `WebDriverWait` + `expected_conditions`，禁止 `sleep()`
- **狀態隔離**：`driver` fixture 為 function scope，`class_driver` 為 class scope，確保測試間互不污染

---

## 環境設定

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

複製 `.env.example` 為 `.env` 並填入測試帳號：

```env
BEANFUN_PURE_ACCOUNT=your_account
BEANFUN_PURE_PASSWORD=your_password
BEANFUN_GP_ACCOUNT=gp_account
BEANFUN_GP_PASSWORD=gp_password
# ... 其他帳號設定
```

### 3. 執行測試

```bash
# 執行全部測試
pytest tests/

# 執行特定模組
pytest tests/test_login_flow.py

# 產生 Allure 報告
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

### 4. Docker 執行

```bash
docker-compose up
```

---

## 報告系統

### Allure 報告
- 失敗案例自動截圖附加至報告
- `categories.json` 區分 Failed / Broken 狀態
- 支援歷史趨勢追蹤（`HistoryReports/`）

### Email 自動報告
執行測試後自動寄送 HTML 格式報告，依「登入測試 / PC版測試」大分類彙整結果，並附上 Allure 報告壓縮檔。

```bash
python send_report.py
```

### 排程自動執行
- 每日 06:00 / 10:15 自動執行（Windows 工作排程器）
- 執行完畢自動寄送報告

```bash
# 安裝排程
install_daily_task_0600.bat
install_daily_task_1015.bat
```

---

## 支援的帳號類型

| 類型 | 說明 |
|---|---|
| 純點帳 | 標準 beanfun 帳號（Yahoo 登入流程）|
| GP 點帳 | 綁定 GamaPass，有雲端背包，含備援帳號 |
| 星帳 | 有雲端背包 |
| bf! 綁定帳 | 需手機 6 碼 OTP 開通 |
| OID 專用帳 | OpenID 流程隔離帳號（與 PC 測試帳號分離）|

---

## 開發規範

本專案嚴格遵守以下規範（詳見 `CLAUDE.md`）：

- 禁止在測試檔直接寫 XPath / CSS Selector
- 禁止使用 `sleep()` 固定等待
- 禁止使用 JavaScript 注入繞過 UI 操作
- 禁止硬編碼帳號密碼
- 每個 Test Case 必須包含 Test ID、標題、步驟、預期結果

---

## License

本專案為個人作品集，僅供展示用途。
