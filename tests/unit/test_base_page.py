"""
Unit Tests：BasePage 核心方法邏輯驗證。

使用 MagicMock 替換真實 WebDriver，不啟動瀏覽器。
重點示範：StaleElementReferenceException 重試機制的正確性。

Test ID 範圍：TC-UNIT-BASE-001 ~ TC-UNIT-BASE-004
"""
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from pages.base_page import BasePage


@pytest.fixture
def base_page():
    """建立帶有 Mock driver 的 BasePage，不啟動真實瀏覽器。"""
    mock_driver = MagicMock()
    return BasePage(mock_driver, timeout=3)


LOCATOR = ("css selector", ".fake-element")


class TestGetText:

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-BASE-001
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_base_001_returns_stripped_text(self, base_page):
        # Test ID: TC-UNIT-BASE-001
        # Test Title: get_text 應回傳去除前後空白的文字
        # Test Steps:
        #   1. Mock wait_until_visible 回傳一個 text 含空白的假元素
        #   2. 呼叫 get_text()
        # Expected Result: 回傳 strip() 後的字串
        mock_element = MagicMock()
        mock_element.text = "  Hello World  "

        with patch.object(base_page, "wait_until_visible", return_value=mock_element):
            result = base_page.get_text(LOCATOR)

        assert result == "Hello World"

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-BASE-002
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_base_002_retries_on_stale_element(self, base_page):
        # Test ID: TC-UNIT-BASE-002
        # Test Title: 第一次取 text 遇到 StaleElementReferenceException 時應自動重試
        # Test Steps:
        #   1. Mock wait_until_visible 第一次回傳的元素，其 .text 屬性拋出 StaleElementReferenceException
        #   2. Mock wait_until_visible 第二次回傳正常元素
        #   3. 呼叫 get_text()
        # Expected Result: 最終成功回傳文字，不拋出例外
        stale_element = MagicMock()
        type(stale_element).text = PropertyMock(side_effect=StaleElementReferenceException)

        fresh_element = MagicMock()
        fresh_element.text = "重試成功"

        with patch.object(base_page, "wait_until_visible", side_effect=[stale_element, fresh_element]):
            result = base_page.get_text(LOCATOR)

        assert result == "重試成功"


class TestIsElementDisplayed:

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-BASE-003
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_base_003_returns_true_when_element_visible(self, base_page):
        # Test ID: TC-UNIT-BASE-003
        # Test Title: 元素可見時 is_element_displayed 應回傳 True
        # Test Steps:
        #   1. Mock WebDriverWait.until 正常回傳（不拋出例外）
        #   2. 呼叫 is_element_displayed()
        # Expected Result: 回傳 True
        with patch("pages.base_page.WebDriverWait") as mock_wait_cls:
            mock_wait_cls.return_value.until.return_value = MagicMock()
            result = base_page.is_element_displayed(LOCATOR)

        assert result is True

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-BASE-004
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_base_004_returns_false_when_element_absent(self, base_page):
        # Test ID: TC-UNIT-BASE-004
        # Test Title: 元素不存在（TimeoutException）時 is_element_displayed 應回傳 False
        # Test Steps:
        #   1. Mock WebDriverWait.until 拋出 TimeoutException
        #   2. 呼叫 is_element_displayed()
        # Expected Result: 回傳 False，不讓例外向上傳播造成測試崩潰
        with patch("pages.base_page.WebDriverWait") as mock_wait_cls:
            mock_wait_cls.return_value.until.side_effect = TimeoutException
            result = base_page.is_element_displayed(LOCATOR)

        assert result is False
