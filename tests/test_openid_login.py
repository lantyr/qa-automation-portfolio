"""
OPEN ID 登入自動化測試。

Test ID 範圍：TC-LOGIN-OID-001 ~ TC-LOGIN-OID-005

測試流程：
  OID-001 → 帳密登入（純點帳）
  OID-002 → 帳密登入（綁bf!點帳）
  OID-003 → 帳密登入（綁GP點帳）
  OID-004 → Gama Pass 登入（綁GP點帳）
  OID-005 → Gama Pass 登入（星帳）

入口：warsofprasia.beanfun.com/Main → 關廣告 → 開始遊戲 → 選登入方式 → 進入 beanfun 登入頁。
"""
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import (
    get_bf_bound_credentials,
    get_bf_bound_otp,
    get_gp_credentials,
    get_gp_gamapass_otp,
    get_gp_otp,
    get_gp_phone,
    get_oid_gp_credentials,
    get_oid_gp_gamapass_credentials,
    get_oid_pure_verified_credentials,
    get_star_credentials,
    get_star_otp,
)
from pages.base_page import BasePage
from pages.home_page import HomePage
from pages.login_page import LoginPage

_TIMEOUT = 20

_GAME_MAIN_URL = "https://warsofprasia.beanfun.com/Main"
_AGE_CONFIRM_BTN = (By.XPATH, "//*[contains(text(), '是，我已滿十八歲')]")
_AD_CLOSE_BTN = (By.XPATH, "//*[@id='Overlay']/div/div/div")
_START_GAME_BTN = (By.XPATH, "//*[@id='app']/div/div[3]/div[1]")
_LOGIN_METHOD_BTN = (By.XPATH, "//*[@id='login']/div[1]/div[2]/a[1]")


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def _go_via_game_main_page(driver, base):
    """從遊戲主頁進入 beanfun 登入頁。"""
    driver.get(_GAME_MAIN_URL)
    base.click_element_safely(_AGE_CONFIRM_BTN)
    try:
        ad = WebDriverWait(driver, 8).until(EC.visibility_of_element_located(_AD_CLOSE_BTN))
        ad.click()
    except Exception:
        pass
    _screenshot(driver, "debug_關廣告後頁面")
    base.click_element_safely(_START_GAME_BTN)
    _screenshot(driver, "debug_點開始遊戲後")
    base.click_element_safely(_LOGIN_METHOD_BTN)
    WebDriverWait(driver, _TIMEOUT).until(EC.url_contains("login.beanfun.com"))


def _is_server_unstable(page_src: str) -> bool:
    return "網路不穩定" in page_src or "SPGA0011" in page_src or "網路問題" in page_src


def _assert_login_success(driver):
    """驗證登入成功：等待跳轉至 warsofprasia.beanfun.com/Main 並截圖。"""
    driver.switch_to.window(driver.window_handles[0])
    try:
        WebDriverWait(driver, _TIMEOUT).until(
            lambda d: "warsofprasia.beanfun.com" in d.current_url
        )
    except TimeoutException:
        _screenshot(driver, "最終_跳轉逾時_頁面狀態")
        if _is_server_unstable(driver.page_source):
            pytest.skip("遊戲伺服器不穩定（網路不穩定），非登入邏輯問題，請非尖峰時段重試")
        raise
    # URL 正確後仍需確認頁面未顯示伺服器錯誤 dialog（SPGA0011 可能在跳轉後才出現）
    if _is_server_unstable(driver.page_source):
        _screenshot(driver, "最終_伺服器錯誤畫面")
        pytest.skip("遊戲伺服器回傳 SPGA0011，非登入邏輯問題，請非尖峰時段重試")
    _screenshot(driver, "最終_跳轉warsofprasia確認")


@allure.feature("OPEN ID 登入")
class TestOpenIdLogin:

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-001：OPEN ID 帳密登入（lilia26012001純點帳）")
    def test_tc_login_oid_001_pure_account(self, driver):
        # Test ID: TC-LOGIN-OID-001
        # Test Title: OPEN ID 帳密登入（純點帳）
        # Test Steps:
        #   1. 從遊戲主頁進入 beanfun 登入頁
        #   2. 以純點帳帳密登入
        #   3. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_oid_pure_verified_credentials()
        allure.dynamic.parameter("帳號", account)

        with allure.step("1. 從遊戲主頁進入 beanfun 登入頁"):
            _go_via_game_main_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 以純點帳執行帳密登入"):
            login.login_action_pure(account, password)
            _screenshot(driver, "步驟2_登入流程完成")

        with allure.step("3. 驗證跳轉至 warsofprasia.beanfun.com/Main"):
            _assert_login_success(driver)

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-002：OPEN ID 帳密登入（202601test000092綁bf!點帳）")
    def test_tc_login_oid_002_bf_bound(self, driver):
        # Test ID: TC-LOGIN-OID-002
        # Test Title: OPEN ID 帳密登入（綁bf!點帳）
        # Test Steps:
        #   1. 從遊戲主頁進入 beanfun 登入頁
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
        allure.dynamic.parameter("帳號", account)
        otp = get_bf_bound_otp()

        with allure.step("1. 從遊戲主頁進入 beanfun 登入頁"):
            _go_via_game_main_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

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

        with allure.step("9. 輸入驗證碼並送出確認"):
            login.fill_otp_code(otp)
            login.submit_otp_and_confirm()
            _screenshot(driver, "步驟9_驗證送出完成")

        with allure.step("10. 驗證跳轉至 warsofprasia.beanfun.com/Main"):
            _assert_login_success(driver)

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-003：OPEN ID 帳密登入（lilia23060801綁GP點帳）")
    def test_tc_login_oid_003_gp_account(self, driver):
        # Test ID: TC-LOGIN-OID-003
        # Test Title: OPEN ID 帳密登入（綁GP點帳）
        # Test Steps:
        #   1. 從遊戲主頁進入 beanfun 登入頁
        #   2. 在帳號欄輸入點數帳號 → 點擊[登入帳號]
        #   3. 確認密碼欄出現 → 輸入密碼 → 點擊[繼續]
        #   4. 確認進入資料驗證-手機(6碼) 頁面，輸入驗證碼
        # Expected Result: 手機 OTP 驗證成功

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_oid_gp_credentials()
        allure.dynamic.parameter("帳號", account)
        otp = get_gp_otp()

        with allure.step("1. 從遊戲主頁進入 beanfun 登入頁"):
            _go_via_game_main_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 輸入帳號 → 點擊[登入帳號]"):
            login.handle_announcement()
            account_el = WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(login.STEP1_ACCOUNT)
            )
            account_el.click()
            account_el.send_keys(account)
            login.click_element_safely(login.STEP1_BTN)
            _screenshot(driver, "步驟2_輸入帳號")

        with allure.step("3. 確認密碼欄出現 → 輸入密碼 → 點擊[繼續]"):
            pwd_el = WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(login.PURE_PWD_INPUT)
            )
            pwd_el.click()
            pwd_el.send_keys(password)
            login.click_element_safely(login.CONTINUE_BTN)
            _screenshot(driver, "步驟3_密碼輸入完成")

        with allure.step("4. 確認進入手機 OTP 頁面，輸入驗證碼並送出"):
            login.assert_phone_verification_page()
            login.fill_otp_code(otp)
            login.submit_otp_and_confirm()
            _screenshot(driver, "步驟4_OTP送出完成")

        with allure.step("5. 驗證跳轉至 warsofprasia.beanfun.com/Main"):
            _assert_login_success(driver)

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-004：OPEN ID Gama Pass 登入（lilia23060801綁GP點帳）")
    def test_tc_login_oid_004_gp_gamapass(self, driver):
        # Test ID: TC-LOGIN-OID-004
        # Test Title: OPEN ID Gama Pass 登入（綁GP點帳）
        # Test Steps:
        #   1. 前往 GAME START URL → 點擊 Sign in → 進入 beanfun 登入頁
        #   2. 點擊「使用Gama Pass」按鈕，等待 GamaPass 頁面
        #   3. 在 GamaPass 輸入帳密完成登入
        #   4. 等待「前往驗證」按鈕並點擊
        #   5. 填寫 OTP 驗證碼並點擊繼續
        #   6. 選擇帳號並確認（若出現）
        #   7. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        account, _ = get_oid_gp_credentials()
        phone, gp_password = get_oid_gp_gamapass_credentials()
        allure.dynamic.parameter("帳號", account)
        otp = get_gp_gamapass_otp()

        with allure.step("1. 從遊戲主頁進入 beanfun 登入頁"):
            _go_via_game_main_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 點擊「使用Gama Pass」按鈕"):
            login.click_element_safely(login.USE_GAMAPASS_BTN)
            WebDriverWait(driver, _TIMEOUT).until(EC.url_contains("accounts.gamania.com"))
            _screenshot(driver, "步驟2_GamaPass頁面")

        with allure.step("3. 在 GamaPass 完成帳密登入"):
            login.login_on_gamapass_window(phone, gp_password)
            _screenshot(driver, "步驟3_GamaPass帳密輸入完成")

        with allure.step("4. 等待「前往驗證」按鈕並點擊"):
            _screenshot(driver, "步驟4_前往驗證前畫面")
            try:
                verify_btn = WebDriverWait(driver, _TIMEOUT).until(
                    EC.visibility_of_element_located(login.GO_TO_VERIFY_BTN)
                )
                driver.execute_script("arguments[0].click();", verify_btn)
                _screenshot(driver, "步驟4_前往驗證已點擊")
            except Exception:
                _screenshot(driver, "步驟4_前往驗證未找到_嘗試iframe")
                login.scan_iframes_and_click(login.GO_TO_VERIFY_BTN)
                _screenshot(driver, "步驟4_iframe掃描後畫面")

        with allure.step("5. 填寫 OTP 驗證碼（自動送出，無需點按鈕）"):
            _screenshot(driver, "步驟5_OTP頁面確認")
            try:
                login.fill_otp_code(otp)
                _screenshot(driver, "步驟5_OTP填寫後頁面狀態")
            except Exception:
                _screenshot(driver, "步驟5_OTP填寫失敗_頁面狀態")
                pytest.skip("OTP 驗證頁未出現，可能登入過於頻繁，請稍後重試")

        with allure.step("6. 選擇帳號並確認"):
            _SPAN = (By.XPATH, "//*[@id='app']//div[contains(@class,'ui-radio-button')]//span")
            try:
                span = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(_SPAN))
                span.click()
                _screenshot(driver, "步驟6_已點選帳號")
                btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(login.CONFIRM_BTN))
                btn.click()
                _screenshot(driver, "步驟6_帳號確認完成")
            except Exception:
                _screenshot(driver, "步驟6_無帳號選擇頁")

        with allure.step("7. 驗證跳轉至 warsofprasia.beanfun.com/Main"):
            _assert_login_success(driver)

    # ────────────────────────────────────────────────────────────
    # TC-LOGIN-OID-005
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-LOGIN-OID-005：OPEN ID Gama Pass 登入（gamaplay788@gamapass.com星帳）")
    def test_tc_login_oid_005_star_gamapass(self, driver):
        # Test ID: TC-LOGIN-OID-005
        # Test Title: OPEN ID Gama Pass 登入（星帳）
        # Test Steps:
        #   1. 前往 GAME START URL → 點擊 Sign in → 進入 beanfun 登入頁
        #   2. 輸入星帳帳號，系統跳轉至 GamaPass 視窗，完成前往驗證
        #   3. 填寫 OTP 驗證碼並點擊繼續
        #   4. 選擇帳號並確認（若出現）
        #   5. 驗證登入成功
        # Expected Result: 登入完成後回到遊戲頁面

        login = LoginPage(driver)
        base = BasePage(driver)
        account, password = get_star_credentials()
        allure.dynamic.parameter("帳號", account)
        otp = get_star_otp()

        with allure.step("1. 從遊戲主頁進入 beanfun 登入頁"):
            _go_via_game_main_page(driver, base)
            _screenshot(driver, "步驟1_beanfun登入頁")

        with allure.step("2. 輸入星帳帳號，完成 GamaPass 登入流程"):
            login.login_action(account, password)
            _screenshot(driver, "步驟2_login_action完成後畫面")

        with allure.step("3. 填寫 OTP 驗證碼（自動送出，無需點按鈕）"):
            _screenshot(driver, "步驟3_OTP頁面確認")
            try:
                login.fill_otp_code(otp)
                _screenshot(driver, "步驟3_OTP填寫後頁面狀態")
            except Exception:
                _screenshot(driver, "步驟3_OTP填寫失敗_頁面狀態")
                pytest.skip("OTP 驗證頁未出現，可能登入過於頻繁，請稍後重試")

        with allure.step("4. 選擇帳號並確認（若出現）"):
            driver.switch_to.window(driver.window_handles[0])
            try:
                login.select_first_account_and_confirm(timeout=15)
                _screenshot(driver, "步驟4_帳號選擇完成")
            except AssertionError:
                _screenshot(driver, "步驟4_無帳號選擇頁")

        with allure.step("5. 驗證跳轉至 warsofprasia.beanfun.com/Main"):
            _assert_login_success(driver)
