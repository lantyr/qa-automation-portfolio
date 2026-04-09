"""
PC 版官網：右側導覽列狀態驗證。

Test ID 範圍：TC-PC-NAV-001 ~ TC-PC-NAV-004
依不同帳號類型驗證導覽列顯示的元素組合：
  001 → 未登入：登入、申請帳號、我的錢包、會員中心
  002 → 純點帳：登出、剩餘點數、會員中心、開通服務
  003 → GP點帳：登出、剩餘點數、會員中心、雲端背包、開通服務
  004 → 星帳：登出、剩餘點數、會員中心、雲端背包、開通服務

每個測試使用獨立 driver（互不影響 session）。
"""
import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import (
    get_beanfun_otp,
    get_gp_credentials,
    get_pure_credentials,
    get_star_credentials,
)
from pages.home_page import HomePage
from pages.login_page import LoginPage


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


@allure.feature("PC版官網導覽列狀態驗證")
class TestPCNavbarStates:

    # ────────────────────────────────────────────────────────────
    # TC-PC-NAV-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-NAV-001：未登入導覽列驗證")
    def test_tc_pc_nav_001_logged_out(self, driver):
        # Test ID: TC-PC-NAV-001
        # Test Title: 未登入導覽列驗證
        # Test Steps:
        #   1. 進入官網首頁（不登入）
        #   2. 驗證導覽列顯示：登入、申請帳號、我的錢包、會員中心
        #   3. 驗證登出按鈕不可見
        # Expected Result: 未登入導覽列元素完整顯示

        home = HomePage(driver)

        with allure.step("1. 進入官網首頁（不登入）"):
            home.go_to_home()
            _screenshot(driver, "步驟1_首頁未登入")

        with allure.step("2. 驗證導覽列顯示：登入、申請帳號、我的錢包、會員中心"):
            home.assert_logged_out_navbar()
            _screenshot(driver, "步驟2_未登入導覽列驗證")

    # ────────────────────────────────────────────────────────────
    # TC-PC-NAV-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-NAV-002：純點帳登入導覽列驗證")
    def test_tc_pc_nav_002_pure_account(self, driver):
        # Test ID: TC-PC-NAV-002
        # Test Title: 純點帳登入導覽列驗證
        # Test Steps:
        #   1. 進入官網，點擊登入
        #   2. 輸入純點帳帳號，點擊「登入帳號」
        #   3. 確認密碼欄出現，輸入密碼，點擊「繼續」
        #   4. 驗證導覽列顯示：登出、剩餘點數、會員中心、開通服務（無雲端背包）
        # Expected Result: 純點帳登入後導覽列元素完整顯示

        home = HomePage(driver)
        login = LoginPage(driver)
        account, password = get_pure_credentials()

        with allure.step("1. 進入官網，點擊登入"):
            home.go_to_home()
            home.click_login_btn()
            _screenshot(driver, "步驟1_點擊登入")

        with allure.step("2-3. 純點帳帳密登入（同視窗流程）"):
            try:
                login.login_action_pure(account, password)
                _screenshot(driver, "步驟2_3_登入完成")
            except Exception:
                _screenshot(driver, "步驟2_3_登入失敗")
                raise

        with allure.step("4. 等待首頁載入並驗證導覽列"):
            WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            home.assert_logged_in_navbar(has_bag=False)
            _screenshot(driver, "步驟4_純點帳導覽列驗證")

    # ────────────────────────────────────────────────────────────
    # TC-PC-NAV-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-NAV-003：GP點帳登入導覽列驗證（有雲端背包）")
    def test_tc_pc_nav_003_gp_account(self, driver):
        # Test ID: TC-PC-NAV-003
        # Test Title: GP點帳登入導覽列驗證（有雲端背包）
        # Test Steps:
        #   1. 進入官網，點擊登入
        #   2. 輸入 GP 點帳帳號，點擊「登入帳號」（開啟 GamaPass 新視窗）
        #   3. 完成 GamaPass 登入流程並填入驗證碼
        #   4. 驗證導覽列顯示：登出、剩餘點數、會員中心、雲端背包、開通服務
        # Expected Result: GP點帳登入後導覽列元素完整顯示（含雲端背包）

        home = HomePage(driver)
        login = LoginPage(driver)
        account, password = get_gp_credentials()
        otp = get_beanfun_otp()

        with allure.step("1. 進入官網，點擊登入"):
            home.go_to_home()
            home.click_login_btn()
            _screenshot(driver, "步驟1_點擊登入")

        with allure.step("2. GamaPass 帳密登入"):
            try:
                login.login_action(account, password, wait_for_verify=False)
                _screenshot(driver, "步驟2_帳密完成")
            except Exception:
                _screenshot(driver, "步驟2_帳密失敗")
                raise

        with allure.step("3. 點擊「前往驗證」"):
            try:
                login.click_element_safely(login.GO_TO_VERIFY_BTN)
                _screenshot(driver, "步驟3_前往驗證點擊")
            except Exception:
                _screenshot(driver, "步驟3_前往驗證失敗")
                raise

        with allure.step("4. 填入 OTP 並確認"):
            try:
                login.fill_otp_code(otp)
                login.click_final_confirm()
                _screenshot(driver, "步驟4_OTP完成")
            except Exception:
                _screenshot(driver, "步驟4_OTP失敗")
                raise

        with allure.step("5. 選取遊戲帳號並確認"):
            try:
                login.select_first_account_and_confirm()
                _screenshot(driver, "步驟5_帳號選擇完成")
            except Exception:
                _screenshot(driver, "步驟5_帳號選擇失敗")
                raise

        with allure.step("6. 等待首頁載入並驗證導覽列"):
            WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            home.assert_logged_in_navbar(has_bag=True)
            _screenshot(driver, "步驟6_GP點帳導覽列驗證")

    # ────────────────────────────────────────────────────────────
    # TC-PC-NAV-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-NAV-004：星帳登入導覽列驗證（有雲端背包）")
    def test_tc_pc_nav_004_star_account(self, driver):
        # Test ID: TC-PC-NAV-004
        # Test Title: 星帳登入導覽列驗證（有雲端背包）
        # Test Steps:
        #   1. 進入官網，點擊登入
        #   2. 輸入星帳帳號，點擊「登入帳號」（開啟 GamaPass 新視窗）
        #   3. 完成 GamaPass 登入流程並填入驗證碼
        #   4. 驗證導覽列顯示：登出、剩餘點數、會員中心、雲端背包、開通服務
        # Expected Result: 星帳登入後導覽列元素完整顯示（含雲端背包）

        home = HomePage(driver)
        login = LoginPage(driver)
        account, password = get_star_credentials()
        otp = get_beanfun_otp()

        with allure.step("1. 進入官網，點擊登入"):
            home.go_to_home()
            home.click_login_btn()
            _screenshot(driver, "步驟1_點擊登入")

        with allure.step("2-3. GamaPass 登入流程"):
            try:
                login.login_action(account, password)
                login.fill_otp_code(otp)
                login.click_final_confirm()
                _screenshot(driver, "步驟2_3_登入完成")
            except Exception:
                _screenshot(driver, "步驟2_3_登入失敗")
                raise

        with allure.step("4. 等待首頁載入並驗證導覽列"):
            WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            home.assert_logged_in_navbar(has_bag=True)
            _screenshot(driver, "步驟4_星帳導覽列驗證")
