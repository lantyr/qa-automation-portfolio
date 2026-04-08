# CLAUDE.md — beanfun 自動化測試專案

## 專案概述

本專案為針對 beanfun 平台（遊戲入口網站）的 UI 自動化測試框架，採用 **Selenium + pytest + Allure** 技術棧，嚴格遵守 **Page Object Model (POM)** 架構。

## 技術棧

- **語言**：Python 3
- **瀏覽器自動化**：Selenium 4
- **測試框架**：pytest 9+
- **報告**：Allure（`allure-pytest`、`allure-combine` 產生單一 HTML）
- **環境變數**：python-dotenv（`.env` 檔案）

## 目錄結構

```
/
├── conftest.py          # pytest fixtures（driver、class_driver）
├── requirements.txt     # 套件依賴
├── run_tests.bat        # 完整執行腳本（pytest → Allure → 封存 → 寄信）
├── send_report.py       # Email 寄送報告
├── pages/               # POM 頁面物件（一頁一檔案，不可含測試邏輯）
│   ├── base_page.py     # BasePage 基底類別（共用等待方法）
│   ├── home_page.py
│   ├── login_page.py
│   └── portal_page.py
├── tests/               # 測試案例（只含測試邏輯，不可寫定位器）
├── config/              # 環境設定、credentials
├── data/                # 測試資料（JSON/CSV，禁止寫死在測試檔中）
├── allure-results/      # pytest 產生的原始結果
├── allure-report/       # allure generate 輸出（含 complete.html）
└── HistoryReports/      # 每次執行封存的 complete.html
```

## 核心架構規範（AI 必須遵守）

### 1. POM 架構
- `/pages` 只放頁面物件：UI 定位器與頁面操作方法，**禁止**含測試斷言。
- `/tests` 只放測試邏輯：透過 Page 物件操作，**禁止**直接在測試中寫 XPath/CSS 定位器。
- 共用工具放 `/utils`，測試資料放 `/data`。

### 2. 等待機制（嚴格禁令）
- **絕對禁止** `time.sleep()` 或任何固定等待。
- 所有等待必須基於元素可見（`visibility_of_element_located`）或可點擊（`element_to_be_clickable`）。
- 遇到無 UI 狀態可偵測時，停止寫程式碼並向使用者討論。

### 3. 禁止 JavaScript 繞過
- **禁止** `driver.execute_script()` 觸發點擊或修改 DOM。
- 若元素被遮擋，先向使用者報告問題，不擅自使用 JS 繞過。

### 4. 測試案例結構
每個 test function 上方必須有完整的 4 要素註解：
```python
# Test ID: TC-XXX
# Test Title: 功能標題
# Test Steps:
#   1. 步驟一
#   2. 步驟二
# Expected Result: 預期結果描述
```

### 5. 測試資料管理
- 帳號、密碼等敏感資訊：透過 `.env` + `python-dotenv` 讀取，**禁止**寫死。
- 其他測試輸入資料：從 `/data` 目錄引入，**禁止**硬編碼在測試檔中。

### 6. DRY 原則
- 重複邏輯抽取為共用函數或 Enum，禁止在多處重複撰寫相同判斷邏輯。
- 檔案路徑、環境變數一律抽為全域設定，禁止寫死。

### 7. 確定性編程
- **禁止**猜測式巢狀 try/except（方法 A 不行試 B 再試 C）。
- 除錯用的 log 或 page_source 印出，找到正確方法後必須全部刪除。

### 8. Flaky Test 處理
- 根治根本原因（動畫延遲、資料未清理等），**禁止**用增加 retry 次數掩蓋問題。

## 執行方式

```bash
# 安裝虛擬環境
setup_venv.bat

# 執行測試（headless 模式，預設開啟）
pytest --alluredir=allure-results

# 執行完整流程（測試 + 報告 + 封存 + 寄信）
run_tests.bat
```

### 環境變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PYTEST_HEADLESS` | `1`/`true` 為無頭模式，`0` 為有頭模式 | `1` |

## AI 協作準則

- 角色定位為 **批判性思考夥伴**，不是單純的程式碼生成器。
- 如果使用者的要求有邏輯錯誤或風險，**有義務**直接提出質疑並建議更好的做法。
- 若有更高效、更穩定、更符合業界標準的寫法，**主動提出**。
