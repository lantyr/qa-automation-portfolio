# 貢獻指南

以下規範是本 repo 架構的基礎，遵守它們可以讓測試套件保持快速、確定、易於維護。

## 架構

1. **Page Object Model 是強制規範。** Locator（`By.ID`、CSS selector、XPath）只能出現在 `src/pages/` 下。測試檔 import page object 並呼叫意圖明確的方法。
2. **測試描述行為，而非實作細節。** 一個測試讀起來應該像一份規格，而不是腳本。如果測試裡出現 XPath 或 sleep，就是錯的。
3. **單一 settings 來源。** 設定集中於 `src/config/settings.py`。測試裡直接讀 `os.getenv` 在 code review 會被擋。

## 同步機制

- **禁止 `time.sleep()`。** 永遠不行。請使用 `WebDriverWait` + `expected_conditions`。
- **等事件，不要等時間。** 可見、可點、不可見、URL 變更 — 選擇真正符合你在等待什麼的條件。
- **如果真的找不到 UI 事件可等，停下來討論。** 不要用 sleep 蒙混過去。

## 使用者互動

- 點真實按鈕、輸入到真實欄位。**禁止用 `execute_script` 繞過 UI**，除非你測的就是 JavaScript 本身。
- 元素被遮擋或不可點？那是 bug，要回報，不是用 JS 繞過。

## 資料

- **禁止硬編碼帳密。** 一律透過 `settings` 從 `.env` 載入。
- **測試資料放 `data/`**，以 JSON 形式存放，測試 parametrize 取用。
- **禁止使用 production 資料。** 本 repo 只測試公開 demo 站。

## 測試結構

每個測試的 docstring 必須包含：

```
ID: PREFIX-NNN
Steps:
  1. ...
  2. ...
Expected: ...
```

Docstring 必須與程式碼一致。改 code 就要改 docstring。

## 負向測試

負向測試是一等公民。用 `@pytest.mark.negative` 標記，並 assert **具體**錯誤訊息，而不是「有東西失敗」。

## Flaky 測試

- Flaky 測試是 bug。找出根本原因（動畫、race condition、髒資料）。
- `pytest-rerunfailures` 在 requirements.txt 是為了應對基礎建設層抖動（CI runner 偶爾抽風），不是用來掩蓋 flakiness。
- 如果找不到根因，請用 `@pytest.mark.xfail(reason="...", strict=True)` 標記並開 issue。

## Code style

- `ruff check .` 必須通過 — CI 會擋。
- 偏好小型、有名稱的方法，而非 inline lambda。
- 公開 API 方法請加 type hints。

## Commit

- 一個 commit 一個邏輯改動。
- Commit message：祈使句現在式（"Add cart badge test"，不是 "Added" 或 "Adds"）。
- 如果 commit 需要一段話解釋「為什麼」，就寫進 commit body。
