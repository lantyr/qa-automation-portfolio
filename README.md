# QA Automation Portfolio

<p align="center">
  <a href="https://github.com/lantyr/qa-automation-portfolio/actions/workflows/ci.yml">
    <img src="https://github.com/lantyr/qa-automation-portfolio/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-1.40+-2EAD33?logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/pytest-8.3+-0A9EDC?logo=pytest&logoColor=white" alt="pytest">
  <img src="https://img.shields.io/badge/Allure-2.13+-FF6B35" alt="Allure">
  <img src="https://img.shields.io/badge/ruff-lint-D7FF64?logo=ruff&logoColor=black" alt="ruff">
</p>

<p align="center">
  以公開 Demo 站為目標的 <strong>API + UI 自動化測試框架</strong>，採用 Page Object Model 架構，整合 Allure 報告，並在每次 push 時透過 GitHub Actions CI 自動驗證。
</p>

---

## 目錄

- [技術棧](#技術棧)
- [測試範圍](#測試範圍)
- [架構設計](#架構設計)
- [環境設定](#環境設定)
- [執行測試](#執行測試)
- [報告系統](#報告系統)
- [CI 流程](#ci-流程)
- [支援的測試 Markers](#支援的測試-markers)
- [開發規範](#開發規範)

---

## 技術棧

| 類別 | 工具 |
|------|------|
| **UI 自動化** | [Playwright](https://playwright.dev/python/)（Chromium，內建自動等待） |
| **API 自動化** | [requests](https://requests.readthedocs.io/) + 自製 ReqResClient 封裝層 |
| **測試框架** | [pytest](https://pytest.org/) + [pytest-xdist](https://github.com/pytest-dev/pytest-xdist)（平行執行） |
| **架構模式** | Page Object Model (POM) |
| **報告系統** | [Allure Report](https://allurereport.org/)（含失敗截圖 + CI artifact 上傳） |
| **Lint** | [ruff](https://docs.astral.sh/ruff/) |
| **環境管理** | python-dotenv |
| **CI/CD** | GitHub Actions（lint → API tests → UI tests） |

---

## 測試範圍

### API 模組 — [reqres.in](https://reqres.in)

| Test ID | 類別 | 測試項目 |
|---------|------|----------|
| USR-001 | Users | 列出使用者（分頁）+ 每筆 JSON Schema 驗證 |
| USR-002 | Users | 取得單一使用者 |
| USR-003 | Users | 取得不存在使用者 → 404 |
| USR-004 | Users | 建立使用者 → 201 + id + createdAt |
| AUT-001 | Auth | 使用者註冊成功 → id + token |
| AUT-002 | Auth | 註冊缺少密碼 → 400 |
| AUT-003 | Auth | 使用者登入成功 → token |
| AUT-004 | Auth | 登入未知使用者 → 400 |
| RBS-001 | Robustness | 回應時間 < 3 秒 |
| RBS-002 | Robustness | Content-Type 為 application/json |
| RBS-003 | Robustness | GET 冪等性驗證 |
| RBS-004 | Robustness | 非法 id 優雅降級（不得 5xx）— parametrize 3 種 |

### UI 模組 — [saucedemo.com](https://www.saucedemo.com)

| Test ID | 類別 | 測試項目 |
|---------|------|----------|
| UI-LOG-001 | Login | 標準帳號登入 → 商品頁 |
| UI-LOG-002 | Login | 被鎖定帳號 → 錯誤訊息 |
| UI-LOG-003 | Login | 錯誤密碼 → 通用錯誤（不洩漏帳號存在性） |
| UI-INV-001 | Inventory | 商品頁列出 6 件商品 |
| UI-INV-002 | Inventory | 排序「價格低→高」驗證遞增 |
| UI-INV-003 | Inventory | 排序「名稱 Z→A」驗證遞減 |
| UI-CHK-001 | Checkout | 加入購物車後 badge 數字更新 |
| UI-CHK-002 | Checkout | 完整結帳流程（登入 → 加購 → 填資料 → 確認） |

---

## 架構設計

```
qa-automation-portfolio/
├── src/
│   ├── api/
│   │   └── reqres_client.py      # API client（requests 封裝，集中 base URL / headers）
│   ├── config/
│   │   └── settings.py           # 型別化設定（frozen dataclass，從 .env 載入）
│   ├── pages/                    # Page Object Model
│   │   ├── base_page.py          # 共用基底（Playwright Page、動態等待）
│   │   ├── login_page.py         # 登入頁
│   │   ├── inventory_page.py     # 商品列表頁
│   │   ├── cart_page.py          # 購物車頁
│   │   └── checkout_page.py      # 結帳頁（Step 1 + Complete）
│   └── utils/
│       └── driver_factory.py     # Playwright 瀏覽器初始化（headless / headed）
├── tests/
│   ├── api/
│   │   ├── test_users.py         # USR-001~004
│   │   ├── test_auth.py          # AUT-001~004
│   │   └── test_robustness.py    # RBS-001~004
│   └── ui/
│       ├── test_login.py         # UI-LOG-001~003
│       ├── test_inventory.py     # UI-INV-001~003
│       └── test_checkout.py      # UI-CHK-001~002
├── data/
│   └── users.json                # 資料驅動用 JSON（帳號、結帳資料）
├── conftest.py                   # pytest hooks、page fixture、自動截圖
├── .github/workflows/ci.yml      # CI 三段：lint → API → UI
├── pytest.ini                    # markers + Allure 設定
├── pyproject.toml                # ruff 設定
├── requirements.txt
├── requirements-dev.txt
└── .env.example                  # 環境變數樣板（無任何密碼）
```

### 核心架構決策

| 決策 | 說明 |
|------|------|
| **嚴格 POM** | 所有 CSS Selector 只存在於 `src/pages/`，測試檔案零 locator |
| **資料驅動** | 帳號、輸入值從 `data/` JSON 載入，敏感資料透過 `.env` 注入，禁止硬編碼 |
| **動態等待** | 全面使用 Playwright 內建自動等待（`locator.wait_for()`），禁止 `sleep()` |
| **狀態隔離** | `driver` fixture 為 function scope，測試間互不污染，支援 `-n auto` 平行執行 |
| **統一 settings** | `src/config/settings.py` 是 frozen dataclass，全 repo 唯一的設定來源 |

---

## 環境設定

### 1. 安裝相依套件

```bash
pip install -r requirements-dev.txt
playwright install chromium --with-deps
```

> `playwright install chromium --with-deps` 只需執行一次，會下載 Chromium 執行檔與所需系統函式庫。

### 2. 設定環境變數

複製 `.env.example` 為 `.env`（**預設值即可直接執行，全為公開 demo 帳號**）：

```bash
cp .env.example .env
```

`.env.example` 內容：

```env
SAUCE_BASE_URL=https://www.saucedemo.com
REQRES_BASE_URL=https://reqres.in/api
SAUCE_USER_STANDARD=standard_user
SAUCE_PASSWORD=secret_sauce
BROWSER_MODE=headless
```

---

## 執行測試

```bash
# 執行全部測試
pytest

# 只跑 API（快，不需要瀏覽器）
pytest -m api

# 只跑 UI smoke
pytest -m "ui and smoke"

# 只跑負向測試
pytest -m negative

# 平行執行
pytest -n auto

# 產生並查看 Allure 報告
pytest --alluredir=allure-results
allure serve allure-results
```

---

## 報告系統

### Allure Report

- UI 測試失敗或 skip 時，自動截圖並附加至 Allure 報告
- Playwright Error 會被轉換為 `AssertionError`，確保 triage 看到的是「Failed（紅）」而非「Broken（黃）」

### CI Artifact

每次 CI 執行（成功或失敗）皆自動上傳 `allure-results/` 為 GitHub Actions artifact，保留 7 天。

---

## CI 流程

`.github/workflows/ci.yml` 在每次 push / PR 觸發：

```
push / PR
    │
    ├── lint          → ruff check .
    ├── api-tests     → pytest tests/api -m api
    └── ui-tests      → playwright install chromium
                        pytest tests/ui -m ui (headless Chromium)
```

---

## 支援的測試 Markers

| Marker | 用途 |
|--------|------|
| `api` | 所有 API 測試 |
| `ui` | 所有 UI 測試（需要瀏覽器） |
| `smoke` | 核心路徑，每次 commit 必須通過 |
| `negative` | 負向 / 錯誤路徑測試 |

---

## 開發規範

- 禁止在測試檔直接寫 CSS Selector — 必須透過 POM
- 禁止使用 `sleep()` 固定等待 — 必須用 Playwright 動態等待
- 禁止使用 JavaScript 注入繞過 UI 操作
- 禁止硬編碼帳號密碼 — 必須透過 `.env`
- 每個 Test Case 必須包含 Test ID、步驟、預期結果（寫在 docstring）
- Flaky test 必須根因處理，禁止用 retry 掩蓋

---

## License

MIT — 見 [LICENSE](LICENSE)。
