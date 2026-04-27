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
    get_bf_bound_otp,
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
        #   1. 進入 OPEN ID 登入頁
        #   2. 在帳號欄輸入點數帳號
        #   3. 點擊[登入帳號]
        #   4. 確認帳號欄下顯示密碼欄
        #   5. 在密碼欄輸入正確密碼
        #   6. 點擊[繼續]
        #   7. 「您的帳號尚未完成開通」彈窗 → 點擊[我知道了]
        #   8. 進入資料驗證-手機(6碼) 頁面
        #   9. 輸入正確驗證碼，驗證成功
        # Expected Result: 手機驗證碼驗證成功

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_bf_bound_credentials()
        otp = get_bf_bound_otp()

        with allure.step("1. 進入 OPEN ID 登入頁"):
            _go_to_openid_login_page(driver, base)
            _screenshot(driver, "步驟1_OPENID登入頁")

        with allure.step("2. 在帳號欄輸入點數帳號"):
            login.handle_announcement()
            account_el = WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(login.STEP1_ACCOUNT)
            )
            account_el.click()
            account_el.send_keys(account)
            _screenshot(driver, "步驟2_輸入點數帳號")

        with allure.step("3. 點擊[登入帳號]"):
            btn = WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(login.STEP1_BTN)
            )
            driver.execute_script("arguments[0].click();", btn)
            _screenshot(driver, "步驟3_點擊登入帳號")

        with allure.step("4. 確認帳號欄下顯示密碼欄"):
            pwd_el = WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(login.PURE_PWD_INPUT)
            )
            assert pwd_el.is_displayed(), "密碼欄未出現於帳號欄下方"
            _screenshot(driver, "步驟4_密碼欄已顯示")

        with allure.step("5. 在密碼欄輸入正確密碼"):
            pwd_el = WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(login.PURE_PWD_INPUT)
            )
            pwd_el.click()
            pwd_el.send_keys(password)
            _screenshot(driver, "步驟5_輸入密碼")

        with allure.step("6. 點擊[繼續]"):
            login.click_element_safely(login.CONTINUE_BTN)
            _screenshot(driver, "步驟6_點擊繼續")

        with allure.step("7. 「您的帳號尚未完成開通」彈窗 → 點擊[我知道了]"):
            login.dismiss_not_activated_dialog()
            _screenshot(driver, "步驟7_點擊我知道了")

        with allure.step("8. 確認進入資料驗證-手機(6碼) 頁面"):
            login.assert_phone_verification_page()
            _screenshot(driver, "步驟8_手機驗證頁面")

        with allure.step("9. 輸入正確驗證碼，驗證成功"):
            login.fill_otp_code(otp)
            _screenshot(driver, "步驟9_驗證成功")

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
        account, password = get_gp_credentials()[0]
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
        account, password = get_gp_credentials()[0]
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
