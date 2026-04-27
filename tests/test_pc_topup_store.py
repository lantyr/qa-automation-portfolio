"""
PC 版官網：儲值與購點彈窗自動化測試。

Test ID 範圍：TC-PC-SP-001 ~ TC-PC-SP-017

測試流程（依操作順序排列）：
  SP-001 → 側欄帳號顯示
  SP-002 → 側欄進階認證狀態顯示（有進階認證）
  SP-003 → 側欄進階認證狀態顯示（無進階認證）
  SP-004 → 側欄重新整理點數功能
  SP-005 → 購買點數頁顯示（未解鎖）
  SP-006 → 序號儲值頁顯示（未解鎖）
  SP-007 → 購買點數頁顯示（已解鎖）
  SP-008 → 序號儲值頁顯示（已解鎖）
  SP-009 → 查詢記錄 - 儲值記錄
  SP-010 → 查詢記錄 - 消費記錄
  SP-011 → 查詢記錄 - 遊戲專用點數
  SP-012 → 查詢記錄 - 最近的儲值紀錄
  SP-013 → 計費設定頁顯示
  SP-014 → 純點帳進階驗證有手機
  SP-015 → GP點帳(1.0)進階驗證有手機
  SP-016 → 星帳(2.0)預設進階驗證
  SP-017 → GP點帳啟動遊戲

資料檔：data/topup_cs_test_data.json
"""
import json
from pathlib import Path

import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import (
    get_beanfun_otp,
    get_gp_credentials,
    get_pure_credentials,
    get_pure_verified_credentials,
    get_star_credentials,
    require_beanfun_credentials,
)
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.topup_popup_page import TopupPopupPage

_DATA_PATH = Path(__file__).parent.parent / "data" / "topup_cs_test_data.json"
with open(_DATA_PATH, encoding="utf-8") as _f:
    _DATA = json.load(_f)

_TIMEOUT = _DATA["element_timeout"]


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


# ════════════════════════════════════════════════════════════════
# SP-001~002, SP-004, SP-007, SP-009~013：認證會員帳號（class_driver 共享）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網儲值與購點")
@pytest.mark.usefixtures("class_driver")
class TestPCTopupStore:
    _login_ok = False

    @pytest.fixture(autouse=True)
    def _inject(self, class_driver):
        self.driver = class_driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)

    def _require_logged_in(self):
        """確認 class_driver 已登入，否則標記為被鎖定跳過。"""
        if not TestPCTopupStore._login_ok:
            pytest.skip("被鎖定：登入 session 未建立（簡訊上限或機器人驗證），請稍後重試")

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-001：側欄帳號顯示")
    def test_tc_pc_sp_001_account_info(self):
        # Test ID: TC-PC-SP-001
        # Test Title: 儲值頁面側欄帳號資訊驗證
        # Test Steps:
        #   前置) 登入 beanfun 帳號
        #   1. 點擊 GASH 點數子選單中的「儲值與購點」
        #   2. 切換至功能操作區域（iframe）
        #   3. 偵測並處理防詐騙 OTP 驗證彈窗
        #   4. 驗證左側帳號資訊區的「剩餘點數」數值可見
        # Expected Result: 帳號資訊區「剩餘點數」可見

        with allure.step("前置：登入 beanfun 帳號"):
            account, password = require_beanfun_credentials()
            otp = get_beanfun_otp()
            self.home.go_to_home()
            self.home.click_login_btn()
            self.login.login_action(account, password)
            try:
                self.login.fill_otp_code(otp)
            except Exception:
                _screenshot(self.driver, "OTP畫面未出現")
                pytest.skip(
                    "beanfun 偵測登入過於頻繁，OTP 驗證頁未出現，請等待數分鐘後重新執行"
                )
            self.login.click_final_confirm()
            WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
            _screenshot(self.driver, "前置_登入完成")

        with allure.step("1. 點擊儲值與購點"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_點擊儲值與購點")

        with allure.step("2. 切換至功能操作區域"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 處理防詐騙彈窗"):
            self.topup.dismiss_anti_fraud_if_present(timeout=5)
            _screenshot(self.driver, "步驟3_防詐騙處理後")

        with allure.step("4. 驗證帳號資訊區剩餘點數可見"):
            self.topup.assert_remaining_points_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟4_剩餘點數可見")
            TestPCTopupStore._login_ok = True

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-002：側欄進階認證狀態顯示（有進階認證）")
    def test_tc_pc_sp_002_verified_member(self):
        # Test ID: TC-PC-SP-002
        # Test Title: 側欄進階認證狀態顯示（有進階認證）
        # Test Steps:
        #   前提) 已登入具進階認證（認證會員）帳號
        #   1. 開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證側欄顯示「認證會員」
        # Expected Result: Remain_point1_lblVerifiedMember 文字包含「認證會員」

        with allure.step("0. 確認已登入"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            if not self.home.is_element_displayed(self.home.LOGOUT_BTN, timeout=3):
                account, password = require_beanfun_credentials()
                otp = get_beanfun_otp()
                self.home.click_login_btn()
                self.home.handle_alert()
                self.login.login_action(account, password)
                try:
                    self.login.fill_otp_code(otp)
                except Exception:
                    pytest.skip("OTP 驗證頁未出現，請等待後重新執行")
                self.login.click_final_confirm()
                WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
                self.home.handle_alert()
                self.home.dismiss_blocking_overlays()
                self.home.go_to_home()

        with allure.step("1. 開啟儲值與購點彈窗"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_開啟彈窗")

        with allure.step("2. 切換至彈窗 iframe"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 驗證側欄顯示認證會員"):
            self.topup.assert_verified_member(_TIMEOUT)
            _screenshot(self.driver, "步驟3_認證會員確認")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-004：側欄重新整理點數功能")
    def test_tc_pc_sp_004_refresh_points(self):
        # Test ID: TC-PC-SP-004
        # Test Title: 更新當前點數
        # Test Steps:
        #   1. 於已開啟的儲值彈窗，切換至功能操作區域
        #   2. 驗證左側帳號資訊區的「當前點數」數值可見
        # Expected Result: 帳號資訊區「當前點數」可見
        self._require_logged_in()

        with allure.step("1. 於已開啟的儲值彈窗，切換至功能操作區域"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 驗證左側帳號資訊區的「當前點數」數值可見"):
            self.topup.assert_current_points_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟2_當前點數可見")

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-007
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-007：購買點數頁顯示（已解鎖）")
    def test_tc_pc_sp_007_buy_points_unlocked(self):
        # Test ID: TC-PC-SP-007
        # Test Title: 購買點數頁顯示（已解鎖）
        # Test Steps:
        #   前提) 已登入認證會員帳號
        #   1. 開啟儲值與購點彈窗，切換至 iframe
        #   2. 點擊左側導覽「購買點數」
        #   3. 驗證支付方式選擇容器（div.type-btns）可見
        # Expected Result: 購買點數頁已解鎖，信用卡／讀卡機轉帳／橘子支付選項顯示
        self._require_logged_in()

        with allure.step("0. 確認已登入"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            if not self.home.is_element_displayed(self.home.LOGOUT_BTN, timeout=3):
                account, password = require_beanfun_credentials()
                otp = get_beanfun_otp()
                self.home.click_login_btn()
                self.home.handle_alert()
                self.login.login_action(account, password)
                try:
                    self.login.fill_otp_code(otp)
                except Exception:
                    pytest.skip("OTP 驗證頁未出現，請等待後重新執行")
                self.login.click_final_confirm()
                WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
                self.home.handle_alert()
                self.home.dismiss_blocking_overlays()
                self.home.go_to_home()

        with allure.step("1. 開啟彈窗並切換至 iframe"):
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 點擊購買點數導覽"):
            self.topup.click_nav_buy_points(_TIMEOUT)
            _screenshot(self.driver, "步驟2_點擊購買點數")

        with allure.step("3. 驗證支付方式選擇容器可見"):
            self.topup.assert_buy_points_unlocked(_TIMEOUT)
            _screenshot(self.driver, "步驟3_支付方式可見")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-009
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-009：查詢記錄 - 儲值記錄")
    def test_tc_pc_sp_009_topup_record(self):
        # Test ID: TC-PC-SP-009
        # Test Title: 查詢記錄 - 儲值記錄
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「儲值記錄」選項
        #   2. 驗證「儲值記錄」頁面內容載入
        # Expected Result: 「儲值記錄」頁面主要內容可見
        self._require_logged_in()

        with allure.step("0. 開啟儲值彈窗並切換至 iframe"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()

        with allure.step("1. 點擊儲值記錄"):
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_TOPUP_RECORD)
            _screenshot(self.driver, "步驟1_點擊儲值記錄")

        with allure.step("2. 驗證頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_儲值記錄頁面內容")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-010
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-010：查詢記錄 - 消費記錄")
    def test_tc_pc_sp_010_consumption_record(self):
        # Test ID: TC-PC-SP-010
        # Test Title: 查詢記錄 - 消費記錄
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「消費記錄」選項
        #   2. 驗證「消費記錄」頁面內容載入
        # Expected Result: 「消費記錄」頁面主要內容可見
        self._require_logged_in()

        with allure.step("0. 開啟儲值彈窗並切換至 iframe"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()

        with allure.step("1. 點擊消費記錄"):
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_CONSUMPTION)
            _screenshot(self.driver, "步驟1_點擊消費記錄")

        with allure.step("2. 驗證頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_消費記錄頁面內容")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-011
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-011：查詢記錄 - 遊戲專用點數")
    def test_tc_pc_sp_011_game_points(self):
        # Test ID: TC-PC-SP-011
        # Test Title: 查詢記錄 - 遊戲專用點數
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「遊戲專用點數」選項
        #   2. 驗證「遊戲專用點數」頁面內容載入
        # Expected Result: 「遊戲專用點數」頁面主要內容可見
        self._require_logged_in()

        with allure.step("0. 開啟儲值彈窗並切換至 iframe"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()

        with allure.step("1. 點擊遊戲專用點數"):
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_GAME_POINTS)
            _screenshot(self.driver, "步驟1_點擊遊戲專用點數")

        with allure.step("2. 驗證頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_遊戲專用點數頁面內容")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-012
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-012：查詢記錄 - 最近的儲值紀錄")
    def test_tc_pc_sp_012_recent_topup(self):
        # Test ID: TC-PC-SP-012
        # Test Title: 查詢記錄 - 最近的儲值紀錄
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「最近儲值記錄」選項
        #   2. 驗證「最近儲值記錄」頁面內容載入
        # Expected Result: 「最近儲值記錄」頁面主要內容可見
        self._require_logged_in()

        with allure.step("0. 開啟儲值彈窗並切換至 iframe"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()

        with allure.step("1. 點擊最近儲值記錄"):
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_RECENT_TOPUP)
            _screenshot(self.driver, "步驟1_點擊最近儲值記錄")

        with allure.step("2. 驗證頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_最近儲值記錄頁面內容")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-013
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-013：計費設定頁顯示")
    def test_tc_pc_sp_013_billing_settings(self):
        # Test ID: TC-PC-SP-013
        # Test Title: 計費設定頁面
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「計費設定」選項
        #   2. 驗證「計費設定」頁面內容載入
        # Expected Result: 「計費設定」頁面主要內容可見
        self._require_logged_in()

        with allure.step("0. 開啟儲值彈窗並切換至 iframe"):
            self.driver.switch_to.default_content()
            self.home.go_to_home()
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()

        with allure.step("1. 點擊計費設定"):
            self.topup.click_nav_item(TopupPopupPage.NAV_BILLING)
            _screenshot(self.driver, "步驟1_點擊計費設定")

        with allure.step("2. 驗證頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_計費設定頁面內容")
            self.driver.switch_to.default_content()


# ════════════════════════════════════════════════════════════════
# SP-003, SP-005, SP-006：一般會員（純點帳 hfivenew）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網儲值與購點")
@pytest.mark.usefixtures("driver")
class TestPCTopupGeneralMember:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        try:
            account, password = get_pure_credentials()
        except ValueError as e:
            pytest.skip(str(e))
        try:
            self.home.go_to_home()
            self.home.click_login_btn()
            self.login.login_action_pure(account, password)
            WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
        except Exception as e:
            pytest.skip(f"純點帳登入失敗，請稍後重試 - {e}")
        yield
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-003：側欄進階認證狀態顯示（無進階認證）")
    def test_tc_pc_sp_003_general_member(self):
        # Test ID: TC-PC-SP-003
        # Test Title: 側欄進階認證狀態顯示（無進階認證）
        # Test Steps:
        #   前提) 已登入一般會員帳號（純點帳 hfivenew）
        #   1. 開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證側欄顯示「一般會員」
        # Expected Result: Remain_point1_lblVerifiedMember 文字包含「一般會員」

        with allure.step("1. 開啟儲值與購點彈窗"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_開啟彈窗")

        with allure.step("2. 切換至彈窗 iframe"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 驗證側欄顯示一般會員"):
            self.topup.assert_general_member(_TIMEOUT)
            _screenshot(self.driver, "步驟3_一般會員確認")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-005
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-005：購買點數頁顯示（未解鎖）")
    def test_tc_pc_sp_005_buy_points_locked(self):
        # Test ID: TC-PC-SP-005
        # Test Title: 購買點數頁顯示（未解鎖）
        # Test Steps:
        #   前提) 已登入一般會員帳號
        #   1. 開啟儲值彈窗，切換至 iframe
        #   2. 點擊左側導覽「購買點數」
        #   3. 驗證顯示「前往認證」按鈕（未解鎖提示）
        # Expected Result: 購買點數頁顯示進階認證提示，「前往認證」按鈕可見

        with allure.step("1. 開啟彈窗並切換至 iframe"):
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 點擊購買點數導覽"):
            self.topup.click_nav_buy_points(_TIMEOUT)
            _screenshot(self.driver, "步驟2_點擊購買點數")

        with allure.step("3. 驗證未解鎖提示出現"):
            self.topup.assert_buy_points_locked(_TIMEOUT)
            _screenshot(self.driver, "步驟3_未解鎖提示")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-006
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-006：儲值彈窗側欄顯示一般會員")
    def test_tc_pc_sp_006_serial_topup_locked(self):
        # Test ID: TC-PC-SP-006
        # Test Title: 儲值彈窗側欄顯示一般會員
        # Test Steps:
        #   前提) 已登入一般會員帳號（純點帳 hfivenew，未進階認證）
        #   1. 開啟儲值彈窗，切換至 iframe
        #   2. 驗證左側側欄顯示「一般會員」
        # Expected Result: Remain_point1_lblVerifiedMember 文字包含「一般會員」
        # 【異動說明】序號儲值導覽項目已由 JS 隱藏（IsWhiteList=false），
        #   改為驗證彈窗側欄正確顯示帳號認證狀態

        with allure.step("1. 開啟彈窗並切換至 iframe"):
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 驗證側欄顯示一般會員"):
            self.topup.assert_general_member(_TIMEOUT)
            _screenshot(self.driver, "步驟2_一般會員確認")
            self.driver.switch_to.default_content()


# ════════════════════════════════════════════════════════════════
# SP-008：序號儲值（已解鎖）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網儲值與購點")
@pytest.mark.usefixtures("driver")
class TestPCTopupSerialUnlocked:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        try:
            account, password = get_pure_verified_credentials()
        except ValueError as e:
            pytest.skip(str(e))
        try:
            self.home.go_to_home()
            self.home.click_login_btn()
            self.login.login_action_pure(account, password)
            WebDriverWait(driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
        except Exception as e:
            pytest.skip(f"認證帳號登入失敗，請稍後重試：{e}")

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-008
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-008：儲值彈窗側欄顯示認證會員")
    def test_tc_pc_sp_008_serial_topup_unlocked(self):
        # Test ID: TC-PC-SP-008
        # Test Title: 儲值彈窗側欄顯示認證會員
        # Test Steps:
        #   前提) 已登入認證會員帳號（純點帳 hfivenew-202601test000101，已進階認證）
        #   1. 開啟儲值彈窗，切換至 iframe
        #   2. 驗證左側側欄顯示「認證會員」
        # Expected Result: Remain_point1_lblVerifiedMember 文字包含「認證會員」
        # 【異動說明】序號儲值導覽項目已由 JS 隱藏（IsWhiteList=true 才顯示），
        #   改為驗證彈窗側欄正確顯示帳號認證狀態

        with allure.step("1. 開啟彈窗並切換至 iframe"):
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 驗證側欄顯示認證會員"):
            self.topup.assert_verified_member(_TIMEOUT)
            _screenshot(self.driver, "步驟2_認證會員確認")
            self.driver.switch_to.default_content()


# ════════════════════════════════════════════════════════════════
# SP-014：純點帳已綁手機進階認證
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網儲值與購點")
class TestPCTopupPureVerifiedAccount:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        account, password = get_pure_verified_credentials()
        try:
            self.home.go_to_home()
            self.home.click_login_btn()
            self.login.login_action_pure(account, password)
            WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
        except Exception as e:
            import pytest as _pytest
            _pytest.skip(f"被鎖定：純點帳（已綁手機）登入失敗，請稍後重試 - {e}")
        yield
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-014
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-014：純點帳進階認證狀態顯示（有手機驗證）")
    def test_tc_pc_sp_014_pure_verified_member(self):
        # Test ID: TC-PC-SP-014
        # Test Title: 純點帳進階認證狀態顯示（有手機驗證）
        # Test Steps:
        #   前提) 已登入純點帳且已綁手機（認證會員）
        #   1. 開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證側欄顯示「認證會員」
        # Expected Result: 側欄顯示認證會員

        with allure.step("1. 開啟儲值與購點彈窗"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_開啟彈窗")

        with allure.step("2. 切換至彈窗 iframe"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 驗證側欄顯示認證會員"):
            self.topup.assert_verified_member(_TIMEOUT)
            _screenshot(self.driver, "步驟3_認證會員確認")
            self.driver.switch_to.default_content()


# ════════════════════════════════════════════════════════════════
# SP-015, SP-017：GP點帳（gamaplay830）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網儲值與購點")
class TestPCTopupGPAccount:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        try:
            candidates = get_gp_credentials()
        except ValueError as e:
            pytest.skip(str(e))
        otp = get_beanfun_otp()
        last_error = None
        for account, password in candidates:
            try:
                # 重試前關閉多餘視窗，確保只剩主視窗
                while len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.home.go_to_home()
                self.home.click_login_btn()
                self.login.login_action(account, password, wait_for_verify=False)
                self.login.click_element_safely(self.login.GO_TO_VERIFY_BTN)
                self.login.fill_otp_code(otp)
                self.login.click_final_confirm()
                try:
                    self.login.select_first_account_and_confirm()
                except AssertionError:
                    pass  # 部分帳號不需要選帳號步驟
                # GamaPass 視窗關閉後切回 beanfun.com 視窗
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(d.window_handles) == 1
                )
                self.driver.switch_to.window(self.driver.window_handles[0])
                WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
                self.home.handle_alert()
                self.home.dismiss_blocking_overlays()
                self.home.go_to_home()
                last_error = None
                break
            except Exception as e:
                last_error = e
        if last_error:
            pytest.skip(f"GP點帳全部登入失敗（主帳＋備援）：{last_error}")
        yield
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-015
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-015：GP點帳(1.0)進階認證狀態顯示（有手機驗證）")
    def test_tc_pc_sp_015_gp_verified_member(self):
        # Test ID: TC-PC-SP-015
        # Test Title: GP點帳(1.0)進階認證狀態顯示（有手機驗證）
        # Test Steps:
        #   前提) 已登入 GP 點帳（gamaplay830，有進階認證）
        #   1. 開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證側欄顯示「認證會員」
        # Expected Result: 側欄顯示認證會員

        with allure.step("1. 開啟儲值與購點彈窗"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_開啟彈窗")

        with allure.step("2. 切換至彈窗 iframe"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 驗證側欄顯示認證會員"):
            self.topup.assert_verified_member(_TIMEOUT)
            _screenshot(self.driver, "步驟3_認證會員確認")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-017
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-017：GP點帳啟動遊戲")
    def test_tc_pc_sp_017_game_start(self):
        # Test ID: TC-PC-SP-017
        # Test Title: GP點帳（gamaplay830）啟動遊戲
        # Test Steps:
        #   前提) 已登入 GP 點帳（gamaplay830，有綁定遊戲帳號）
        #   1. 前往首頁（已登入 GP 帳號）
        #   2. 點擊快速啟動，開啟遊戲選擇彈窗
        #   3. 點擊遊戲，觸發啟動遊戲
        #   4. 驗證跳轉至 game_zone 頁面
        # Expected Result: 點擊啟動遊戲後，跳轉至 game_zone

        with allure.step("1. 前往首頁（已登入 GP 帳號）"):
            self.home.go_to_home()
            _screenshot(self.driver, "步驟1_首頁GP登入")

        with allure.step("2. 點擊快速啟動，開啟遊戲選擇彈窗"):
            self.home.click_quick_start()
            self.home.wait_until_visible(HomePage.QUICK_START_GAME_LI)
            _screenshot(self.driver, "步驟2_彈窗出現")

        with allure.step("3. 點擊遊戲，觸發啟動遊戲"):
            current_url = self.driver.current_url
            self.home.click_first_game_in_popup()
            _screenshot(self.driver, "步驟3_點擊遊戲")

        with allure.step("4. 驗證跳轉至 game_zone 頁面"):
            WebDriverWait(self.driver, _TIMEOUT).until(EC.url_contains("game_zone"))
            _screenshot(self.driver, "步驟4_game_zone已載入")


# ════════════════════════════════════════════════════════════════
# SP-016：星帳（gamaplay788）進階認證
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網儲值與購點")
class TestPCTopupStarAccount:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        try:
            account, password = get_star_credentials()
        except ValueError as e:
            pytest.skip(str(e))
        otp = get_beanfun_otp()
        try:
            self.home.go_to_home()
            self.home.click_login_btn()
            self.login.login_action(account, password)
            self.login.fill_otp_code(otp)
            self.login.click_final_confirm()
            WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
        except Exception as e:
            import pytest as _pytest
            _pytest.skip(f"被鎖定：星帳登入失敗，請稍後重試 - {e}")
        yield
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-016
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-016：星帳(2.0)預設進階認證狀態顯示")
    def test_tc_pc_sp_016_star_verified_member(self):
        # Test ID: TC-PC-SP-016
        # Test Title: 星帳(2.0)預設進階認證狀態顯示
        # Test Steps:
        #   前提) 已登入星帳（gamaplay788，預設有進階認證）
        #   1. 開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證側欄顯示「認證會員」
        # Expected Result: 側欄顯示認證會員

        with allure.step("1. 開啟儲值與購點彈窗"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_開啟彈窗")

        with allure.step("2. 切換至彈窗 iframe"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 驗證側欄顯示認證會員"):
            self.topup.assert_verified_member(_TIMEOUT)
            _screenshot(self.driver, "步驟3_認證會員確認")
            self.driver.switch_to.default_content()


# ════════════════════════════════════════════════════════════════
# SP-001：純點帳已綁手機（000101）進階認證狀態驗證
# ════════════════════════════════════════════════════════════════
@allure.feature("PC版儲值彈窗 - 純點帳進階認證（有手機）")
class TestPCTopupPureVerifiedSP001:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        try:
            account, password = get_pure_verified_credentials()
        except ValueError as e:
            pytest.skip(str(e))
        try:
            self.home.go_to_home()
            self.home.click_login_btn()
            self.login.login_action_pure(account, password)
            WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
        except Exception as e:
            import pytest as _pytest
            _pytest.skip(f"被鎖定：純點帳（已綁手機）登入失敗，請稍後重試 - {e}")
        yield
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    @allure.title("TC-PC-SP-001：純點帳進階認證狀態顯示（有手機驗證）")
    def test_tc_pc_sp_001_pure_verified_member(self):
        # Test ID: TC-PC-SP-001
        # Test Title: 純點帳進階認證狀態顯示（有手機驗證）
        # Test Steps:
        #   前提) 已登入純點帳且已綁手機（hfivenew-000101，認證會員）
        #   1. 開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證側欄顯示「認證會員」
        # Expected Result: 側欄顯示認證會員

        with allure.step("1. 開啟儲值與購點彈窗"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_開啟彈窗")

        with allure.step("2. 切換至彈窗 iframe"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟2_切換iframe")

        with allure.step("3. 驗證側欄顯示認證會員"):
            self.topup.assert_verified_member(_TIMEOUT)
            _screenshot(self.driver, "步驟3_認證會員確認")
            self.driver.switch_to.default_content()
