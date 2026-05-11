"""
共登(PC)：帳密登入自動化測試。

Test ID 範圍：TC-LOGIN-PC-001

測試流程：
  PC-001 → 純點帳帳密登入成功
"""
import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import get_pure_verified_credentials
from pages.home_page import HomePage
from pages.login_page import LoginPage

_TIMEOUT = 20


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


@allure.feature("共登PC-帳密登入")
class TestPasswordLogin:

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-PC-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-PC-001：純點帳帳密登入成功")
    def test_tc_login_pc_001_pure_account(self, driver):
        # Test ID: TC-LOGIN-PC-001
        # Test Title: 純點帳帳密登入成功
        # Test Steps:
        #   1. 前往首頁，點擊登入按鈕
        #   2. 於登入頁輸入純點帳帳號密碼，點擊繼續
        #   3. 驗證登入成功（登出按鈕可見）
        # Expected Result: 純點帳成功登入，首頁顯示登出按鈕

        home = HomePage(driver)
        login = LoginPage(driver)
        account, password = get_pure_verified_credentials()
        allure.dynamic.parameter("帳號", account)

        with allure.step("1. 前往首頁並點擊登入"):
            home.go_to_home()
            home.click_login_btn()
            _screenshot(driver, "步驟1_點擊登入")

        with allure.step("2. 以純點帳執行帳密登入"):
            login.login_action_pure(account, password)
            WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(HomePage.LOGOUT_BTN)
            )
            home.handle_alert()
            home.dismiss_blocking_overlays()
            _screenshot(driver, "步驟2_登入流程完成")

        with allure.step("3. 驗證登入成功（登出按鈕可見）"):
            home.go_to_home()
            assert home.is_element_displayed(home.LOGOUT_BTN, timeout=_TIMEOUT), \
                "登入後應顯示登出按鈕"
            _screenshot(driver, "步驟3_登出按鈕可見")
