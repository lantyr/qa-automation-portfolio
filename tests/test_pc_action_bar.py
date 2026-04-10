"""
PC 版官網：Action Bar 自動化測試。

Test ID 範圍：
  TC-PC-NAV-001~004  導覽列狀態顯示（未登入 / 各帳號類型）
  TC-PC-HOME-015~016 已登入後 Action Bar 操作

涵蓋功能：
  NAV-001 → 未登入導覽列顯示
  NAV-002 → 純點帳登入導覽列顯示
  NAV-003 → GP點帳登入導覽列顯示（含雲端背包）
  NAV-004 → 星帳登入導覽列顯示（含雲端背包）
  HOME-015 → 點擊雲端背包開啟新分頁
  HOME-016 → 點擊開通服務開啟任務儀表板彈窗
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
    require_beanfun_credentials,
)
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.topup_popup_page import TopupPopupPage

_TIMEOUT = 20


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


# ════════════════════════════════════════════════════════════════
# 導覽列狀態顯示（TC-PC-NAV-001~004）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網Action Bar")
class TestPCActionBarDisplay:

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
        #   2. 純點帳帳密登入
        #   3. 驗證導覽列顯示：登出、剩餘點數、會員中心、開通服務（無雲端背包）
        # Expected Result: 純點帳登入後導覽列元素完整顯示

        home = HomePage(driver)
        login = LoginPage(driver)
        account, password = get_pure_credentials()

        with allure.step("1. 進入官網，點擊登入"):
            home.go_to_home()
            home.click_login_btn()
            _screenshot(driver, "步驟1_點擊登入")

        with allure.step("2-3. 純點帳帳密登入（同視窗流程）"):
            login.login_action_pure(account, password)
            _screenshot(driver, "步驟2_3_登入完成")

        with allure.step("4. 等待首頁載入並驗證導覽列"):
            WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            _screenshot(driver, "步驟4_純點帳導覽列驗證")
            home.assert_logged_in_navbar(has_bag=False)

    # ────────────────────────────────────────────────────────────
    # TC-PC-NAV-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-NAV-003：GP點帳登入導覽列驗證（有雲端背包）")
    def test_tc_pc_nav_003_gp_account(self, driver):
        # Test ID: TC-PC-NAV-003
        # Test Title: GP點帳登入導覽列驗證（有雲端背包）
        # Test Steps:
        #   1. 進入官網，點擊登入
        #   2. GamaPass 帳密登入
        #   3. 點擊「前往驗證」
        #   4. 填入 OTP 並確認
        #   5. 選取遊戲帳號並確認
        #   6. 驗證導覽列顯示：登出、剩餘點數、會員中心、雲端背包、開通服務
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
            login.login_action(account, password, wait_for_verify=False)
            _screenshot(driver, "步驟2_帳密完成")

        with allure.step("3. 點擊「前往驗證」"):
            login.click_element_safely(login.GO_TO_VERIFY_BTN)
            _screenshot(driver, "步驟3_前往驗證點擊")

        with allure.step("4. 填入 OTP 並確認"):
            login.fill_otp_code(otp)
            login.click_final_confirm()
            _screenshot(driver, "步驟4_OTP完成")

        with allure.step("5. 選取遊戲帳號並確認"):
            login.select_first_account_and_confirm()
            _screenshot(driver, "步驟5_帳號選擇完成")

        with allure.step("6. 等待首頁載入並驗證導覽列"):
            WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            _screenshot(driver, "步驟6_GP點帳導覽列驗證")
            home.assert_logged_in_navbar(has_bag=True)

    # ────────────────────────────────────────────────────────────
    # TC-PC-NAV-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-NAV-004：星帳登入導覽列驗證（有雲端背包）")
    def test_tc_pc_nav_004_star_account(self, driver):
        # Test ID: TC-PC-NAV-004
        # Test Title: 星帳登入導覽列驗證（有雲端背包）
        # Test Steps:
        #   1. 進入官網，點擊登入
        #   2. GamaPass 登入流程
        #   3. 驗證導覽列顯示：登出、剩餘點數、會員中心、雲端背包、開通服務
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
            login.login_action(account, password)
            login.fill_otp_code(otp)
            login.click_final_confirm()
            _screenshot(driver, "步驟2_3_登入完成")

        with allure.step("4. 等待首頁載入並驗證導覽列"):
            WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
            home.handle_alert()
            home.dismiss_blocking_overlays()
            home.go_to_home()
            _screenshot(driver, "步驟4_星帳導覽列驗證")
            home.assert_logged_in_navbar(has_bag=True)


# ════════════════════════════════════════════════════════════════
# 已登入後 Action Bar 操作（TC-PC-HOME-015~016）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網Action Bar")
class TestPCActionBarLoggedIn:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(driver)
        self.login = LoginPage(driver)
        self.topup = TopupPopupPage(driver)

        account, password = require_beanfun_credentials()
        otp = get_beanfun_otp()
        self.home.go_to_home()
        self.home.click_login_btn()
        self.login.login_action(account, password)
        try:
            self.login.fill_otp_code(otp)
        except Exception:
            pytest.skip("beanfun OTP 驗證頁未出現，請等待數分鐘後重新執行")
        self.login.click_final_confirm()
        WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
        self.home.handle_alert()
        self.home.dismiss_blocking_overlays()

    # ────────────────────────────────────────────────────────────
    # TC-PC-HOME-015
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HOME-015：點擊雲端背包開啟新分頁")
    def test_tc_pc_home_015_bag(self):
        # Test ID: TC-PC-HOME-015
        # Test Title: 點擊雲端背包開啟新分頁
        # Test Steps:
        #   1. 前往首頁，點擊「雲端背包」按鈕
        #   2. 驗證新分頁已開啟且 URL 包含 Backpack
        # Expected Result: 新分頁 URL 包含 Backpack 路徑

        with allure.step("1. 前往首頁並點擊雲端背包"):
            self.home.go_to_home()
            original_handles = self.driver.window_handles
            self.home.click_bag_btn()
            _screenshot(self.driver, "步驟1_點擊雲端背包")

        with allure.step("2. 驗證新分頁開啟且 URL 包含 Backpack"):
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.window_handles) > len(original_handles)
            )
            self.driver.switch_to.window(self.driver.window_handles[-1])
            WebDriverWait(self.driver, 10).until(EC.url_contains("Backpack"))
            _screenshot(self.driver, "步驟2_新分頁URL驗證")
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    # ────────────────────────────────────────────────────────────
    # TC-PC-HOME-016
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HOME-016：點擊開通服務開啟任務儀表板彈窗")
    def test_tc_pc_home_016_open_service(self):
        # Test ID: TC-PC-HOME-016
        # Test Title: 點擊開通服務開啟任務儀表板彈窗
        # Test Steps:
        #   1. 前往首頁，點擊「開通服務」按鈕
        #   2. 驗證 fbContent 彈窗出現
        #   3. 切換至彈窗 iframe，驗證頁面為 MissionDashBoard
        # Expected Result: fbContent 彈窗出現，iframe 內含 MissionDashBoard form

        with allure.step("1. 前往首頁並點擊開通服務"):
            self.home.go_to_home()
            self.home.click_open_service()
            _screenshot(self.driver, "步驟1_點擊開通服務")

        with allure.step("2. 驗證 fbContent 彈窗出現"):
            self.topup.assert_popup_root_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟2_彈窗出現")

        with allure.step("3. 驗證 iframe 內為 MissionDashBoard"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            WebDriverWait(self.driver, _TIMEOUT).until(
                EC.presence_of_element_located(self.home.MISSION_DASHBOARD_FORM)
            )
            _screenshot(self.driver, "步驟3_MissionDashBoard確認")
            self.driver.switch_to.default_content()

    # TC-PC-HOME-001~014 待補（登入、快速啟動遊戲、剩餘點數顯示、開啟會員中心、
    #                          開啟儲值與購點、重整點數、登出 等）
