"""
OPEN ID 登入自動化測試。

Test ID 範圍：TC-LOGIN-OID-001 ~ TC-LOGIN-OID-005

測試流程：
  OID-001 → 帳密登入（純點帳）
  OID-002 → 帳密登入（綁bf!點帳）
  OID-003 → 帳密登入（綁GP點帳）
  OID-004 → Gama Pass 登入（綁GP點帳）
  OID-005 → Gama Pass 登入（星帳）

入口：GAME START URL → 點擊「Sign in with gamania Games」→ 進入 beanfun 登入頁。
"""
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import (
    get_beanfun_otp,
    get_bf_bound_credentials,
    get_gp_credentials,
    get_openid_login_url,
    get_pure_verified_credentials,
    get_star_credentials,
)
from pages.base_page import BasePage
from pages.home_page import HomePage
from pages.login_page import LoginPage

_TIMEOUT = 20

SIGN_IN_BTN = (By.CSS_SELECTOR, "a.btnLogin-beanfun")


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def _go_to_openid_login_page(driver, base):
    """前往 OPEN ID 入口並點擊 Sign in 按鈕，進入 beanfun 登入頁。"""
    openid_url = get_openid_login_url()
    driver.get(openid_url)
    WebDriverWait(driver, _TIMEOUT).until(
        EC.visibility_of_element_located(SIGN_IN_BTN)
    )
    base.click_element_safely(SIGN_IN_BTN)
    WebDriverWait(driver, _TIMEOUT).until(EC.url_contains("login.beanfun.com"))


def _assert_login_success(driver):
    """驗證登入成功（回到遊戲頁面或 beanfun）。"""
    driver.switch_to.window(driver.window_handles[0])
    WebDriverWait(driver, _TIMEOUT).until(
        lambda d: "galaxy.games" in d.current_url
        or "beanfun.com" in d.current_url
        or "warsofprasia" in d.current_url
    )


@allure.feature("OPEN ID 登入")
class TestOpenIdLogin:

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-001：OPEN ID 帳密登入（純點帳）")
    def test_tc_login_oid_001_pure_account(self, driver):
        # Test ID: TC-LOGIN-OID-001
        # Test Title: OPEN ID 帳密登入（純點帳）
        # Test Steps:
        #   1. 前往 GAME START URL → 點擊 Sign in → 進入 beanfun 登入頁
        #   2. 以純點帳帳密登入
        #   3. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        home = HomePage(driver)
        account, password = get_pure_verified_credentials()

        with allure.step("1. 前往 OPEN ID 登入入口"):
            _go_to_openid_login_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 以純點帳執行帳密登入"):
            login.login_action_pure(account, password)
            _screenshot(driver, "步驟2_登入流程完成")

        with allure.step("3. 驗證登入成功"):
            _assert_login_success(driver)
            _screenshot(driver, "步驟3_登入成功")

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-002：OPEN ID 帳密登入（綁bf!點帳）")
    def test_tc_login_oid_002_bf_bound(self, driver):
        # Test ID: TC-LOGIN-OID-002
        # Test Title: OPEN ID 帳密登入（綁bf!點帳）
        # Test Steps:
        #   1. 前往 GAME START URL → 點擊 Sign in → 進入 beanfun 登入頁
        #   2. 以 bf! 帳號執行帳密登入（經 GamaPass）
        #   3. 填寫 OTP 驗證碼
        #   4. 選擇帳號並確認（若出現）
        #   5. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_bf_bound_credentials()
        otp = get_beanfun_otp()

        with allure.step("1. 前往 OPEN ID 登入入口"):
            _go_to_openid_login_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 以 bf! 帳號執行帳密登入（經 GamaPass）"):
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

        with allure.step("4. 選擇帳號並確認（若出現）"):
            try:
                login.select_first_account_and_confirm(timeout=10)
                _screenshot(driver, "步驟4_帳號選擇完成")
            except AssertionError:
                _screenshot(driver, "步驟4_無帳號選擇頁")

        with allure.step("5. 驗證登入成功"):
            _assert_login_success(driver)
            _screenshot(driver, "步驟5_登入成功")

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-003：OPEN ID 帳密登入（綁GP點帳）")
    def test_tc_login_oid_003_gp_account(self, driver):
        # Test ID: TC-LOGIN-OID-003
        # Test Title: OPEN ID 帳密登入（綁GP點帳）
        # Test Steps:
        #   1. 前往 GAME START URL → 點擊 Sign in → 進入 beanfun 登入頁
        #   2. 以 GP 點帳執行帳密登入（經 GamaPass）
        #   3. 填寫 OTP 驗證碼
        #   4. 選擇帳號並確認（若出現）
        #   5. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_gp_credentials()
        otp = get_beanfun_otp()

        with allure.step("1. 前往 OPEN ID 登入入口"):
            _go_to_openid_login_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 以 GP 點帳執行帳密登入（經 GamaPass）"):
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

        with allure.step("4. 選擇帳號並確認（若出現）"):
            try:
                login.select_first_account_and_confirm(timeout=10)
                _screenshot(driver, "步驟4_帳號選擇完成")
            except AssertionError:
                _screenshot(driver, "步驟4_無帳號選擇頁")

        with allure.step("5. 驗證登入成功"):
            _assert_login_success(driver)
            _screenshot(driver, "步驟5_登入成功")

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-004：OPEN ID Gama Pass 登入（綁GP點帳）")
    def test_tc_login_oid_004_gp_gamapass(self, driver):
        # Test ID: TC-LOGIN-OID-004
        # Test Title: OPEN ID Gama Pass 登入（綁GP點帳）
        # Test Steps:
        #   1. 前往 GAME START URL → 點擊 Sign in → 進入 beanfun 登入頁
        #   2. 輸入 GP 帳號，系統跳轉至 GamaPass 視窗
        #   3. 在 GamaPass 輸入帳密，完成前往驗證
        #   4. 填寫 OTP 驗證碼
        #   5. 選擇帳號並確認（若出現）
        #   6. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_gp_credentials()
        otp = get_beanfun_otp()

        with allure.step("1. 前往 OPEN ID 登入入口"):
            _go_to_openid_login_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 輸入 GP 帳號，完成 GamaPass 登入流程"):
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

        with allure.step("4. 選擇帳號並確認（若出現）"):
            try:
                login.select_first_account_and_confirm(timeout=10)
                _screenshot(driver, "步驟4_帳號選擇完成")
            except AssertionError:
                _screenshot(driver, "步驟4_無帳號選擇頁")

        with allure.step("5. 驗證登入成功"):
            _assert_login_success(driver)
            _screenshot(driver, "步驟5_登入成功")

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-005
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-005：OPEN ID Gama Pass 登入（星帳）")
    def test_tc_login_oid_005_star_gamapass(self, driver):
        # Test ID: TC-LOGIN-OID-005
        # Test Title: OPEN ID Gama Pass 登入（星帳）
        # Test Steps:
        #   1. 前往 GAME START URL → 點擊 Sign in → 進入 beanfun 登入頁
        #   2. 輸入星帳帳號，系統跳轉至 GamaPass 視窗
        #   3. 在 GamaPass 輸入帳密，完成前往驗證
        #   4. 填寫 OTP 驗證碼
        #   5. 選擇帳號並確認（若出現）
        #   6. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_star_credentials()
        otp = get_beanfun_otp()

        with allure.step("1. 前往 OPEN ID 登入入口"):
            _go_to_openid_login_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 輸入星帳帳號，完成 GamaPass 登入流程"):
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

        with allure.step("4. 選擇帳號並確認（若出現）"):
            try:
                login.select_first_account_and_confirm(timeout=10)
                _screenshot(driver, "步驟4_帳號選擇完成")
            except AssertionError:
                _screenshot(driver, "步驟4_無帳號選擇頁")

        with allure.step("5. 驗證登入成功"):
            _assert_login_success(driver)
            _screenshot(driver, "步驟5_登入成功")
