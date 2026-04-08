"""
PC 版官網：客服中心自動化測試。

Test ID 範圍：TC-PC-CS-001
測試從首頁頁尾入口進入客服中心，不需要登入即可執行。

資料檔：data/topup_cs_test_data.json
"""
import json
from pathlib import Path

import allure
import pytest

import config.credentials  # noqa: F401 - 載入 .env
from pages.home_page import HomePage

_DATA_PATH = Path(__file__).parent.parent / "data" / "topup_cs_test_data.json"
with open(_DATA_PATH, encoding="utf-8") as _f:
    _DATA = json.load(_f)

_TIMEOUT = _DATA["element_timeout"]
_CS_CFG = _DATA["customer_service"]


@allure.feature("PC版官網客服中心")
class TestPCCustomerService:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)

    # ────────────────────────────────────────────────────────────
    # TC-PC-CS-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-CS-001：驗證客服中心入口可見可點擊並進入")
    def test_tc_pc_cs_001_enter_customer_service(self):
        # Test ID: TC-PC-CS-001
        # Test Title: 驗證客服中心入口可見可點擊並進入
        # Test Steps:
        #   1. 向下滾動頁面至底部區域
        #   2. 驗證底部的「客服中心」入口按鈕存在、可見且可點擊
        #   3. 點擊「客服中心」入口按鈕，驗證成功進入客服中心頁面並截圖
        # Expected Result: 成功進入客服中心頁面，URL 或標題包含預期關鍵字

        with allure.step("1. 向下滾動頁面至底部區域"):
            self.home.go_to_home()
            self.home.scroll_to_footer()

        with allure.step("2. 驗證底部的「客服中心」入口按鈕存在、可見且可點擊"):
            self.home.wait_until_clickable(HomePage.FOOTER_CS_LINK)

        with allure.step("3. 點擊「客服中心」入口按鈕，驗證成功進入客服中心頁面並截圖"):
            original_url = self.driver.current_url
            self.home.click_footer_customer_service()

            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            WebDriverWait(self.driver, _TIMEOUT).until(
                EC.url_changes(original_url)
            )

            current_url = self.driver.current_url
            page_title = self.driver.title
            assert (
                _CS_CFG["expected_url_fragment"] in current_url
                or _CS_CFG["expected_title_fragment"] in page_title
            ), (
                f"預期 URL 包含 '{_CS_CFG['expected_url_fragment']}' 或"
                f" 標題包含 '{_CS_CFG['expected_title_fragment']}'，"
                f"實際 URL={current_url}，Title={page_title}"
            )

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="客服中心頁面截圖",
                attachment_type=allure.attachment_type.PNG,
            )
