"""
PC 版官網：右側功能列（Action Bar）自動化測試。

Test ID 範圍：TC-PC-AB-001 ~ TC-PC-AB-013

涵蓋功能（依操作流程排序）：
  AB-001 → 未登入導覽列顯示
  AB-002 → 已登入顯示（純點帳）
  AB-003 → 已登入顯示（GP點帳，含雲端背包）
  AB-004 → 已登入顯示（星帳，含雲端背包）
  AB-005 → 點擊登入跳轉至登入頁面
  AB-006 → 快速啟動遊戲（GP帳號）
  AB-007 → 剩餘點數顯示
  AB-008 → 開啟會員中心
  AB-009 → 開啟儲值與購點
  AB-010 → 重整點數（GP帳號）
  AB-011 → 點擊雲端背包
  AB-012 → 點擊開通服務
  AB-013 → 登出
"""
import allure
import pytest
from selenium.common.exceptions import TimeoutException
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
from pages.member_center_page import MemberCenterPage

_TIMEOUT = 20


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


# ════════════════════════════════════════════════════════════════
# 導覽列狀態顯示（TC-PC-AB-001~004）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網右側功能列")
class TestPCActionBarDisplay:

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-001：未登入導覽列驗證")
    def test_tc_pc_ab_001_logged_out(self, driver):
        # Test ID: TC-PC-AB-001
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
    # TC-PC-AB-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-002：純點帳登入導覽列驗證")
    def test_tc_pc_ab_002_pure_account(self, driver):
        # Test ID: TC-PC-AB-002
        # Test Title: 已登入顯示（純點帳）
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
    # TC-PC-AB-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-003：GP點帳登入導覽列驗證（有雲端背包）")
    def test_tc_pc_ab_003_gp_account(self, driver):
        # Test ID: TC-PC-AB-003
        # Test Title: 已登入顯示（GP點帳，含雲端背包）
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
            try:
                login.fill_otp_code(otp)
            except Exception:
                _screenshot(driver, "OTP驗證失敗")
                pytest.skip("GP帳號 OTP 驗證頁未出現（簡訊上限或機器人攔截），請稍後重試")
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
    # TC-PC-AB-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-004：星帳登入導覽列驗證（有雲端背包）")
    def test_tc_pc_ab_004_star_account(self, driver):
        # Test ID: TC-PC-AB-004
        # Test Title: 已登入顯示（星帳，含雲端背包）
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

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-005
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-005：點擊登入跳轉至登入頁面")
    def test_tc_pc_ab_005_login_redirect(self, driver):
        # Test ID: TC-PC-AB-005
        # Test Title: 點擊登入按鈕跳轉至登入頁面
        # Test Steps:
        #   1. 進入官網首頁（不登入）
        #   2. 點擊「登入」按鈕
        #   3. 驗證頁面跳轉至 login.beanfun.com/Login/Index
        # Expected Result: 當前 URL 包含 login.beanfun.com/Login/Index

        home = HomePage(driver)

        with allure.step("1. 進入官網首頁"):
            home.go_to_home()
            _screenshot(driver, "步驟1_首頁未登入")

        with allure.step("2. 點擊登入按鈕"):
            home.click_login_btn()
            _screenshot(driver, "步驟2_點擊登入")

        with allure.step("3. 驗證跳轉至登入頁面"):
            WebDriverWait(driver, _TIMEOUT).until(
                EC.url_contains("login.beanfun.com/Login/Index")
            )
            _screenshot(driver, "步驟3_登入頁面")


# ════════════════════════════════════════════════════════════════
# 已登入後右側功能列操作（TC-PC-AB-007~009、011~013）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網右側功能列")
@pytest.mark.usefixtures("class_driver")
class TestPCActionBarLoggedIn:
    _login_ok = False

    @pytest.fixture(autouse=True)
    def _setup(self, class_driver):
        self.driver = class_driver
        self.home = HomePage(class_driver)
        self.login = LoginPage(class_driver)
        self.topup = TopupPopupPage(class_driver)
        self.member = MemberCenterPage(class_driver)

        if not TestPCActionBarLoggedIn._login_ok:
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
            WebDriverWait(class_driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            TestPCActionBarLoggedIn._login_ok = True
        else:
            self.driver.switch_to.default_content()
            self.home.go_to_home_if_needed()
            self.home.dismiss_blocking_overlays()

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-007
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-007：剩餘點數顯示驗證")
    def test_tc_pc_ab_007_remaining_points(self):
        # Test ID: TC-PC-AB-007
        # Test Title: 已登入後右側功能列剩餘點數顯示驗證
        # Test Steps:
        #   1. 前往首頁
        #   2. 驗證 BF_btnGash（我的錢包）可見
        #   3. 驗證 BF_RemainPoint span 顯示為數字
        # Expected Result: BF_RemainPoint 內容為純數字

        with allure.step("1. 前往首頁"):
            self.home.go_to_home()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 驗證我的錢包按鈕可見"):
            self.home.wait_until_visible(HomePage.REMAINING_POINTS_TOGGLE)
            _screenshot(self.driver, "步驟2_我的錢包可見")

        with allure.step("3. 驗證 BF_RemainPoint 顯示數字"):
            remain_el = self.home.wait_until_visible(HomePage.REMAIN_POINT)
            text = remain_el.text.strip()
            assert text.isdigit(), f"BF_RemainPoint 內容應為數字，實際為：{text}"
            _screenshot(self.driver, "步驟3_點數數字確認")

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-008
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-008：點擊會員中心開啟會員中心彈窗")
    def test_tc_pc_ab_008_open_member_center(self):
        # Test ID: TC-PC-AB-008
        # Test Title: 點擊右側功能列「會員中心」開啟 fbContent 彈窗
        # Test Steps:
        #   1. 前往首頁
        #   2. 點擊「會員中心」按鈕（BF_btnMember）
        #   3. 驗證 fbContent 彈窗出現
        # Expected Result: fbContent 彈窗成功開啟

        with allure.step("1. 前往首頁"):
            self.home.go_to_home()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 點擊會員中心"):
            self.home.click_member_center()
            _screenshot(self.driver, "步驟2_點擊會員中心")

        with allure.step("3. 驗證 fbContent 彈窗出現"):
            self.member.assert_popup_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟3_會員中心彈窗已開啟")

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-009
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-009：點擊儲值與購點開啟彈窗")
    def test_tc_pc_ab_009_open_topup(self):
        # Test ID: TC-PC-AB-009
        # Test Title: 點擊右側功能列「儲值與購點」開啟儲值彈窗
        # Test Steps:
        #   1. 前往首頁
        #   2. 點擊「我的錢包/GASH」展開子選單，點擊「儲值與購點」
        #   3. 驗證 fbContent 彈窗出現
        # Expected Result: 儲值與購點彈窗（fbContent）成功開啟

        with allure.step("1. 前往首頁"):
            self.home.go_to_home()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 點擊儲值與購點"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟2_點擊儲值與購點")

        with allure.step("3. 驗證彈窗出現"):
            self.topup.assert_popup_root_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟3_彈窗已出現")

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-011
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-011：點擊雲端背包開啟新分頁")
    def test_tc_pc_ab_011_bag(self):
        # Test ID: TC-PC-AB-011
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
    # TC-PC-AB-012
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-012：點擊開通服務開啟任務儀表板彈窗")
    def test_tc_pc_ab_012_open_service(self):
        # Test ID: TC-PC-AB-012
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

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-013
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-013：點擊登出回到未登入狀態")
    def test_tc_pc_ab_013_logout(self):
        # Test ID: TC-PC-AB-013
        # Test Title: 點擊登出後導覽列回到未登入狀態
        # Test Steps:
        #   1. 前往首頁（已登入）
        #   2. 點擊「登出」按鈕（BF_btnLogout）
        #   3. 接受「是否要登出遊戲橘子」確認彈窗
        #   4. 等待登出完成，驗證導覽列回到未登入狀態
        # Expected Result: 登出成功，申請帳號（BF_btnSignup）恢復顯示，登出按鈕消失

        with allure.step("1. 前往首頁（已登入）"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            self.home.dismiss_blocking_overlays()
            _screenshot(self.driver, "步驟1_首頁已登入")

        with allure.step("2. 點擊登出"):
            self.home.click_element_safely(HomePage.LOGOUT_BTN)
            _screenshot(self.driver, "步驟2_點擊登出")

        with allure.step("3. 接受登出確認彈窗"):
            from selenium.common.exceptions import NoAlertPresentException
            try:
                WebDriverWait(self.driver, _TIMEOUT).until(EC.alert_is_present())
                self.driver.switch_to.alert.accept()
            except (TimeoutException, NoAlertPresentException):
                pass
            _screenshot(self.driver, "步驟3_確認登出")

        with allure.step("4. 驗證導覽列回到未登入狀態"):
            WebDriverWait(self.driver, _TIMEOUT).until(
                EC.invisibility_of_element_located(HomePage.LOGOUT_BTN)
            )
            self.home.go_to_home()
            self.home.assert_logged_out_navbar()
            _screenshot(self.driver, "步驟4_未登入狀態確認")


# ════════════════════════════════════════════════════════════════
# GP 帳號登入後操作（TC-PC-AB-006、010）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網右側功能列")
@pytest.mark.usefixtures("class_driver")
class TestPCActionBarGPAccount:
    _login_ok = False

    @pytest.fixture(autouse=True)
    def _setup(self, class_driver):
        self.driver = class_driver
        self.home = HomePage(class_driver)
        self.login = LoginPage(class_driver)
        self.topup = TopupPopupPage(class_driver)

        if not TestPCActionBarGPAccount._login_ok:
            account, password = get_gp_credentials()
            otp = get_beanfun_otp()
            try:
                self.home.go_to_home()
                self.home.click_login_btn()
                self.login.login_action(account, password, wait_for_verify=False)
                self.login.click_element_safely(self.login.GO_TO_VERIFY_BTN)
                self.login.fill_otp_code(otp)
                self.login.click_final_confirm()
                self.login.select_first_account_and_confirm()
                WebDriverWait(class_driver, _TIMEOUT).until(EC.url_contains("beanfun.com"))
                self.home.handle_alert()
                self.home.dismiss_blocking_overlays()
                self.home.go_to_home()
                TestPCActionBarGPAccount._login_ok = True
            except Exception as e:
                pytest.skip(f"GP帳號登入失敗（OTP 速率限制或帳號問題），請稍後重試：{e}")
        else:
            self.driver.switch_to.default_content()
            self.home.go_to_home_if_needed()
            self.home.dismiss_blocking_overlays()

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-006
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-006：快速啟動遊戲按鈕可見並可點擊")
    def test_tc_pc_ab_006_quick_start(self):
        # Test ID: TC-PC-AB-006
        # Test Title: GP帳號登入後快速啟動遊戲按鈕可見並可點擊
        # Test Steps:
        #   1. 前往首頁（已登入 GP 帳號）
        #   2. 驗證 BF_btnQuickStart（快速啟動）可見
        #   3. 點擊快速啟動，驗證彈窗出現
        #   4. 驗證彈窗內有遊戲清單（至少一筆）
        # Expected Result: BF_btnQuickStart 可見，點擊後彈窗出現並含遊戲清單

        with allure.step("1. 前往首頁（已登入 GP 帳號）"):
            self.home.go_to_home()
            _screenshot(self.driver, "步驟1_首頁GP登入")

        with allure.step("2. 驗證快速啟動按鈕可見"):
            self.home.wait_until_visible(HomePage.QUICK_START_BTN)
            _screenshot(self.driver, "步驟2_快速啟動按鈕可見")

        with allure.step("3. 點擊快速啟動，驗證彈窗出現"):
            self.home.click_quick_start()
            self.home.wait_until_visible(HomePage.QUICK_START_POPUP)
            _screenshot(self.driver, "步驟3_彈窗出現")

        with allure.step("4. 驗證彈窗內有遊戲清單（至少一筆）"):
            items = self.driver.find_elements(*HomePage.QUICK_START_GAME_LI)
            assert len(items) > 0, "快速啟動彈窗內找不到任何遊戲"
            _screenshot(self.driver, "步驟4_遊戲清單確認")

    # ────────────────────────────────────────────────────────────
    # TC-PC-AB-010
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-AB-010：儲值彈窗內點擊更新點數")
    def test_tc_pc_ab_010_refresh_points(self):
        # Test ID: TC-PC-AB-010
        # Test Title: 開啟儲值彈窗後點擊「更新點數」重整點數顯示
        # Test Steps:
        #   1. 前往首頁，開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證「更新點數」span 可見並點擊
        #   4. 驗證剩餘點數區塊仍可見（更新完成）
        # Expected Result: 點擊更新點數後，剩餘點數區塊維持可見

        with allure.step("1. 前往首頁，開啟儲值彈窗"):
            self.home.go_to_home()
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_開啟彈窗")

        with allure.step("2. 切換至彈窗 iframe"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 驗證更新點數可見並點擊"):
            self.topup.click_refresh_points(_TIMEOUT)
            _screenshot(self.driver, "步驟3_點擊更新點數")

        with allure.step("4. 驗證剩餘點數區塊仍可見"):
            self.topup.assert_remaining_points_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟4_點數區塊仍可見")
            self.driver.switch_to.default_content()
