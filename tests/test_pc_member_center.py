"""
PC 版官網：會員中心自動化測試。

涵蓋範圍（依操作流程排序）：
  MC-001 → GP帳進入會員中心（gamaplay830，無服務開通）
  MC-002 → 星帳進入會員中心（gamaplay788，有帳號整合分頁）
"""
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import get_beanfun_otp, get_gp_credentials, get_star_credentials
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.member_center_page import MemberCenterPage

_TIMEOUT = 20


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def _login_gp(home, login):
    """GP帳登入流程（含 OTP + 選帳號）。"""
    account, password = get_gp_credentials()[0]
    otp = get_beanfun_otp()
    home.go_to_home()
    home.click_login_btn()
    login.login_action(account, password, wait_for_verify=False)
    try:
        login.click_element_safely(login.GO_TO_VERIFY_BTN)
        login.fill_otp_code(otp)
    except Exception:
        pytest.skip("beanfun OTP 驗證頁未出現（已達當日上限），請等待後重新執行")
    login.click_final_confirm()
    try:
        login.select_first_account_and_confirm()
    except AssertionError:
        pass
    WebDriverWait(home.driver, _TIMEOUT).until(
        EC.visibility_of_element_located(HomePage.LOGOUT_BTN)
    )
    home.handle_alert()
    home.dismiss_blocking_overlays()


def _login_star(home, login):
    """星帳登入流程（含 OTP + 選帳號）。"""
    account, password = get_star_credentials()
    otp = get_beanfun_otp()
    home.go_to_home()
    home.click_login_btn()
    login.login_action(account, password, wait_for_verify=False)
    try:
        login.click_element_safely(login.GO_TO_VERIFY_BTN)
        login.fill_otp_code(otp)
    except Exception:
        pytest.skip("beanfun OTP 驗證頁未出現（已達當日上限），請等待後重新執行")
    login.click_final_confirm()
    try:
        login.select_first_account_and_confirm()
    except AssertionError:
        pass
    WebDriverWait(home.driver, _TIMEOUT).until(
        EC.visibility_of_element_located(HomePage.LOGOUT_BTN)
    )
    home.handle_alert()
    home.dismiss_blocking_overlays()


# ════════════════════════════════════════════════════════════════
# 會員中心（TC-PC-MC-001~002）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網會員中心")
class TestPCMemberCenter:

    # ────────────────────────────────────────────────────────────
    # TC-PC-MC-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-MC-001：GP帳點擊會員中心開啟 fbContent 彈窗")
    def test_tc_pc_mc_001_gp_member_center(self, driver):
        # Test ID: TC-PC-MC-001
        # Test Title: GP帳點擊會員中心開啟會員中心彈窗
        # Test Steps:
        #   1. GP帳登入
        #   2. 前往首頁，點擊「會員中心」按鈕
        #   3. 驗證 fbContent 彈窗出現
        #   4. 切換至 fbContent iframe，驗證會員清單側欄可見
        # Expected Result: 會員中心彈窗成功開啟，側欄可見

        home = HomePage(driver)
        login = LoginPage(driver)
        member = MemberCenterPage(driver)

        with allure.step("1. GP帳登入"):
            _login_gp(home, login)
            _screenshot(driver, "步驟1_GP帳登入完成")

        with allure.step("2. 前往首頁，點擊會員中心按鈕"):
            home.go_to_home()
            home.click_member_center()
            _screenshot(driver, "步驟2_點擊會員中心")

        with allure.step("3. 驗證 fbContent 彈窗出現"):
            member.assert_popup_visible(_TIMEOUT)
            _screenshot(driver, "步驟3_彈窗出現")

        with allure.step("4. 切換至 iframe，驗證會員清單側欄可見"):
            member.switch_to_iframe(_TIMEOUT)
            member.assert_member_list_visible(_TIMEOUT)
            _screenshot(driver, "步驟4_側欄可見")
            driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-MC-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-MC-002：星帳點擊會員中心，驗證帳號整合分頁存在")
    def test_tc_pc_mc_002_star_member_center(self, driver):
        # Test ID: TC-PC-MC-002
        # Test Title: 星帳點擊會員中心，驗證帳號整合分頁可見
        # Test Steps:
        #   1. 星帳登入
        #   2. 前往首頁，點擊「會員中心」按鈕
        #   3. 驗證 fbContent 彈窗出現
        #   4. 切換至 iframe，驗證「帳號整合」分頁可見
        # Expected Result: 星帳會員中心彈窗開啟，且帳號整合分頁存在

        STAR_ACCOUNT_INTEGRATION = (By.CSS_SELECTOR, "a.memberItemTitle.targetBtn[data-page='2']")

        home = HomePage(driver)
        login = LoginPage(driver)
        member = MemberCenterPage(driver)

        with allure.step("1. 星帳登入"):
            _login_star(home, login)
            _screenshot(driver, "步驟1_星帳登入完成")

        with allure.step("2. 前往首頁，點擊會員中心按鈕"):
            home.go_to_home()
            home.click_member_center()
            _screenshot(driver, "步驟2_點擊會員中心")

        with allure.step("3. 驗證 fbContent 彈窗出現"):
            member.assert_popup_visible(_TIMEOUT)
            _screenshot(driver, "步驟3_彈窗出現")

        with allure.step("4. 切換至 iframe，驗證帳號整合分頁可見"):
            member.switch_to_iframe(_TIMEOUT)
            WebDriverWait(driver, _TIMEOUT).until(
                EC.visibility_of_element_located(STAR_ACCOUNT_INTEGRATION)
            )
            _screenshot(driver, "步驟4_帳號整合分頁可見")
            driver.switch_to.default_content()
