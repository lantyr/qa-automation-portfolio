# GamaPass Automation Test Framework

> 獨立設計並實作的 **beanfun GamaPass PC 官網** UI 自動化測試框架，採用 Page Object Model 架構，覆蓋登入、會員中心、儲值等 13 個測試模組，支援 CI/CD 排程執行與多層次自動化報告系統。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.41+-green)
![pytest](https://img.shields.io/badge/pytest-9.0+-orange)
![Allure](https://img.shields.io/badge/Allure-2.15+-yellow)
![Docker](https://img.shields.io/badge/Docker-支援-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-black)

---

## 專案概覽

| 項目 | 內容 |
|---|---|
| 測試模組 | 13 個 |
| 測試案例 | 100+ TC |
| 測試框架 | pytest + Selenium WebDriver 4.x |
| 架構模式 | Page Object Model (POM) |
| 報告系統 | Allure Report + HTML Email 自動寄送 |
| 執行環境 | GitHub Actions / Docker / Windows 排程 |
| 設計者 | 獨立設計與實作 |

---

## 技術棧

| 分類 | 工具 |
|---|---|
| UI 自動化 | Selenium WebDriver 4.x |
| 測試框架 | pytest + allure-pytest |
| 容器化 | Docker + docker-compose |
| CI/CD | GitHub Actions |
| 報告系統 | Allure Report、HTML Email、Google Drive 備份 |
| 環境管理 | python-dotenv |
| 語言 | Python 3.10+ |

---

## 架構設計

```
GamaAutomation/
├── pages/                      # Page Object Model — 唯一存放 locator 的地方
│   ├── base_page.py            # 核心基底類別（動態等待、安全點擊、防 Flaky 機制）
│   ├── home_page.py            # 首頁操作
│   ├── login_page.py           # 登入流程（支援 5 種帳號類型）
│   ├── member_center_page.py   # 會員中心
│   ├── topup_popup_page.py     # 儲值購點彈窗
│   └── portal_page.py          # GamaPass 入口頁
│
├── tests/                      # 純測試邏輯，不含任何 locator
│   ├── test_login_flow.py      # TC-LOGIN-PC 系列
│   ├── test_openid_login.py    # TC-LOGIN-OID 系列
│   ├── test_negative_login.py  # TC-NEGATIVE 系列
│   ├── test_migration_login.py # TC-MIGRATE 系列
│   ├── test_api_gamapass_login.py # TC-API 系列
│   ├── test_pc_homepage.py     # TC-PC-HOME 系列
│   ├── test_pc_action_bar.py   # TC-PC-ACTION-BAR 系列
│   ├── test_pc_sidebar.py      # SC-P / SC-S 系列（43 TC）
│   ├── test_pc_topup_store.py  # TC-PC-SP 系列（17 TC）
│   ├── test_pc_member_center.py
│   ├── test_pc_customer_service.py
│   ├── test_pc_navbar_states.py
│   └── test_homepage_video.py
│
├── config/
│   └── credentials.py          # 帳號憑證管理（從 .env 讀取，禁止硬編碼）
│
├── data/                       # 測試資料（JSON），與測試邏輯完全分離
│
├── conftest.py                 # pytest hooks、WebDriver fixture、失敗自動截圖
├── categories.json             # Allure Failed / Broken 狀態分類規則
├── send_report.py              # HTML Email 報告自動寄送
├── inject_trend_table.py       # 跨次執行 pass rate 趨勢分析
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 核心設計決策

### 1. 嚴格 POM 分層

測試檔案（`tests/`）**完全不含任何 XPath / CSS Selector**，所有定位器集中在對應的 Page 類別中管理。

```python
# tests/test_login_flow.py — 測試層只描述行為
def test_tc_login_pc_001_pure_account(self, driver):
    home = HomePage(driver)
    login = LoginPage(driver)
    home.go_to_home()
    home.click_login_btn()
    login.login_action_pure(account, password)
    assert home.is_element_displayed(home.LOGOUT_BTN)

# pages/login_page.py — 定位器只存在 Page 層
STEP1_ACCOUNT = (By.XPATH, "//input[@placeholder='請輸入帳號']")
PURE_PWD_INPUT = (By.XPATH, "//input[@placeholder='請輸入密碼']")
```

### 2. 防 Flaky 的動態等待機制

`BasePage` 封裝三層防禦，根治不穩定測試的根本原因：

```python
def click_element_safely(self, locator):
    # 自動忽略 ElementClickInterceptedException（元素被遮擋）
    # 自動忽略 StaleElementReferenceException（DOM 重整）
    # 直到成功點擊或超時才拋出明確的 AssertionError
    safe_wait = WebDriverWait(
        self.driver, self.timeout,
        poll_frequency=0.5,
        ignored_exceptions=[
            ElementClickInterceptedException,
            StaleElementReferenceException
        ]
    )
```

### 3. 429 速率限制自動處理

偵測到 beanfun IP 封鎖時，**自動等待冷卻並重試**，無需人工介入排程恢復。

```python
def check_for_rate_limit(self):
    if '429' in title or 'Too Many Requests' in src:
        time.sleep(900)  # 等待 15 分鐘冷卻（伺服器端行為，無 UI 狀態可偵測）
        self.driver.refresh()
```

### 4. 環境變數驅動，禁止硬編碼

所有帳號、密碼、OTP 皆透過 `.env` 注入，支援多種帳號類型：

| 帳號類型 | 說明 |
|---|---|
| 純點帳 | 標準 beanfun 帳號 |
| GP 點帳 | 綁定 GamaPass，含備援帳號 |
| 星帳 | 有雲端背包 |
| bf! 綁定帳 | 需手機 6 碼 OTP |
| OID 專用帳 | OpenID 流程隔離帳號 |

---

## 測試範圍

### 登入模組

| Test ID | 測試項目 |
|---|---|
| TC-LOGIN-PC-001 | 純點帳帳密登入 |
| TC-LOGIN-OID-001~005 | OpenID 登入（5 種帳號類型）|
| TC-MIGRATE | 帳號遷移登入流程 |
| TC-NEGATIVE | 負向測試（錯誤帳密、邊界案例）|
| TC-API | API 層級 GamaPass 登入驗證 |

### PC 版功能模組

| Test ID 範圍 | 測試項目 | TC 數量 |
|---|---|---|
| TC-PC-HOME | 首頁功能驗證、影片播放 | 多 |
| TC-PC-ACTION-BAR | 右側功能列操作 | 多 |
| SC-P-001~021 | 純點帳會員中心側欄 | 21 |
| SC-S-001~022 | 星帳會員中心側欄 | 22 |
| TC-PC-SP-001~017 | 儲值與購點彈窗 | 17 |
| TC-PC-MC | 會員中心頁面驗證 | 多 |
| TC-PC-CS | 客服中心頁面驗證 | 多 |
| TC-PC-NAVBAR | 導覽列狀態驗證 | 多 |

---

## 執行流程與 CI/CD Pipeline

```
開發者 Push / 排程觸發
        ↓
GitHub Actions / Windows 排程器
        ↓
Docker 容器啟動（headless Chrome）
        ↓
pytest 執行測試（分批執行避免速率限制）
        ↓
        ├─→ Allure Results 產生
        │       ↓
        │   Allure Report 生成（含歷史趨勢）
        │       ↓
        │   Google Drive 備份
        │
        └─→ send_report.py
                ↓
            HTML Email 自動寄送
            （依登入 / PC 版分類彙整）
```

### 分批執行機制

為避免 beanfun 速率限制，測試依模組分批執行：

```bash
run_batch1.bat   # 登入模組
run_batch2.bat   # 首頁 / 功能列
run_batch3.bat   # 會員中心 / 儲值
```

---

## 報告系統

### Allure Report
- 失敗案例**自動截圖**附加至報告
- `categories.json` 區分 **Failed**（測試邏輯失敗）/ **Broken**（環境/框架異常）
- 支援**歷史趨勢追蹤**（`HistoryReports/`），可視化每次執行的 pass rate 變化

### HTML Email 自動報告
- 依「登入測試 / PC 版測試」大分類彙整結果
- 包含各模組通過率統計
- 附上 Allure 報告壓縮檔

---

## 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
cp .env.example .env
# 填入測試帳號資訊
```

### 3. 執行測試

```bash
# 執行全部測試並產生 Allure 報告
pytest tests/ --alluredir=allure-results

# 執行特定模組
pytest tests/test_login_flow.py -v

# 開啟 Allure 報告
allure serve allure-results
```

### 4. Docker 執行

```bash
docker-compose up
```

### 5. 寄送報告

```bash
python send_report.py
```

---

## 開發規範

本專案嚴格遵守以下原則（詳見 `CLAUDE.md`）：

| 規範 | 說明 |
|---|---|
| 嚴格 POM | 所有 locator 只存在於 `pages/`，測試檔案零 locator |
| 禁止硬編碼 | 帳號密碼全部透過 `.env` 環境變數注入 |
| 動態等待 | 全面使用 `WebDriverWait`，禁止 `sleep()` 固定等待 |
| 資料驅動 | 測試資料從 `data/` 目錄的 JSON 檔讀取 |
| 狀態隔離 | `driver` fixture 為 function scope，測試間完全隔離 |

---

## License

本專案為個人作品集，僅供展示用途。
