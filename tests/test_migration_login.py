"""
共登(PC)：Gama Pass 登入自動化測試。

Test ID 範圍：TC-LOGIN-PC-002 ~ TC-LOGIN-PC-003

測試流程：
  PC-002 → GP點帳透過 Gama Pass 登入成功
  PC-003 → 星帳透過 Gama Pass 登入成功（需選擇遊戲帳號）

入口與帳密登入相同（在 Portal 頁輸入帳號 → 點「登入帳號」），
差別在系統偵測到 GP/星帳後跳轉至 GamaPass 視窗，需再貼一次帳號完成登入。
"""
import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import get_beanfun_otp, get_gp_credentials, get_star_credentials
from pages.home_page import HomePage
from pages.login_page import LoginPage

_TIMEOUT = 20


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def _switch_to_main_window(driver):
    """切回最初的主視窗（index 0）。"""
    main = driver.window_handles[0]
    driver.switch_to.window(main)


@allure.feature("共登PC-Gama Pass登入")
class TestGamaPassLogin:

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-PC-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-PC-002：GP點帳透過 Gama Pass 登入成功")
    def test_tc_login_pc_002_gp_account(self, driver):
        # Test ID: TC-LOGIN-PC-002
        # Test Title: GP點帳透過 Gama Pass 登入成功
        # Test Steps:
        #   1. 前往首頁，點擊登入按鈕
        #   2. 輸入GP點帳帳號，系統跳轉至 GamaPass 視窗
        #   3. 在 GamaPass 再次輸入帳號與密碼，完成前往驗證
        #   4. 填寫 OTP 驗證碼（若需要）
        #   5. 選擇帳號（若出現）
        #   6. 驗證登入成功（登出按鈕可見）
        # Expected Result: GP點帳透過 GamaPass 成功登入

        home = HomePage(driver)
        login = LoginPage(driver)
        account, password = get_gp_credentials()[0]
        otp = get_beanfun_otp()

        with allure.step("1. 前往首頁並點擊登入"):
            home.go_to_home()
            home.click_login_btn()
            _screenshot(driver, "步驟1_點擊登入")

        with allure.step("2. 輸入GP點帳，完成 GamaPass 登入流程"):
            login.login_action(account, password)
            _screenshot(driver, "步驟2_GamaPass前往驗證完成")

        with allure.step("3. 填寫 OTP 驗證碼"):
            try:
                login.fill_otp_code(otp)
            except Exception:
                _screenshot(driver, "OTP畫面未出現")
                pytest.skip("OTP 驗證頁未出現，可能登入過於頻繁，請稍後重試")
            login.click_final_confirm()
            _screenshot(driver, "步驟3_OTP填寫完成")

        with allure.step("4. 選擇帳號（若出現）"):
            try:
                login.select_first_account_and_confirm(timeout=10)
                _screenshot(driver, "步驟4_帳號選擇完成")
            except AssertionError:
                _screenshot(driver, "步驟4_無帳號選擇頁")

        with allure.step("5. 驗證登入成功"):
            _switch_to_main_window(driver)
            WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(HomePage.LOGOUT_BTN)
            )
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            assert home.is_element_displayed(home.LOGOUT_BTN, timeout=_TIMEOUT), \
                "登入後應顯示登出按鈕"
            _screenshot(driver, "步驟5_登入成功")

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-PC-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-PC-003：星帳透過 Gama Pass 登入成功（選擇遊戲帳號）")
    def test_tc_login_pc_003_star_account(self, driver):
        # Test ID: TC-LOGIN-PC-003
        # Test Title: 星帳透過 Gama Pass 登入成功（需選擇遊戲帳號）
        # Test Steps:
        #   1. 前往首頁，點擊登入按鈕
        #   2. 輸入星帳帳號，系統跳轉至 GamaPass 視窗
        #   3. 在 GamaPass 再次輸入帳號與密碼，完成前往驗證
        #   4. 填寫 OTP 驗證碼
        #   5. 選擇遊戲帳號並確認（若出現）
        #   6. 驗證登入成功
        # Expected Result: 星帳選擇遊戲帳號後成功登入

        home = HomePage(driver)
        login = LoginPage(driver)
        account, password = get_star_credentials()
        otp = get_beanfun_otp()

        with allure.step("1. 前往首頁並點擊登入"):
            home.go_to_home()
            home.click_login_btn()
            _screenshot(driver, "步驟1_點擊登入")

        with allure.step("2. 輸入星帳，完成 GamaPass 登入流程"):
            login.login_action(account, password)
            _screenshot(driver, "步驟2_GamaPass前往驗證完成")

        with allure.step("3. 填寫 OTP 驗證碼"):
            try:
                login.fill_otp_code(otp)
            except Exception:
                _screenshot(driver, "OTP畫面未出現")
                pytest.skip("OTP 驗證頁未出現，可能登入過於頻繁，請稍後重試")
            login.click_final_confirm()
            _screenshot(driver, "步驟3_OTP填寫完成")

        with allure.step("4. 選擇遊戲帳號（若出現）"):
            try:
                login.select_first_account_and_confirm(timeout=10)
                _screenshot(driver, "步驟4_帳號選擇完成")
            except AssertionError:
                _screenshot(driver, "步驟4_無帳號選擇頁（可能已自動選取）")

        with allure.step("5. 驗證登入成功"):
            _switch_to_main_window(driver)
            WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(HomePage.LOGOUT_BTN)
            )
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            assert home.is_element_displayed(home.LOGOUT_BTN, timeout=_TIMEOUT), \
                "登入後應顯示登出按鈕"
            _screenshot(driver, "步驟5_登入成功")
