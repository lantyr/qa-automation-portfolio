"""
PC 版官網：儲值與購點彈窗自動化測試。

Test ID 範圍：TC-PC-SP-001 ~ TC-PC-SP-010
測試流程為共用同一個瀏覽器 session（class_driver）的連續操作：
  001 → 登入並開啟彈窗
  002 → 切換 iframe、處理防詐騙彈窗、驗證帳號資訊
  003~008 → 逐一點擊左側導覽並驗證頁面載入
  009 → 驗證當前點數
  010 → 關閉彈窗

資料檔：data/topup_cs_test_data.json
"""
import json
from pathlib import Path

import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import get_beanfun_otp, require_beanfun_credentials
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.topup_popup_page import TopupPopupPage

_DATA_PATH = Path(__file__).parent.parent / "data" / "topup_cs_test_data.json"
with open(_DATA_PATH, encoding="utf-8") as _f:
    _DATA = json.load(_f)

_TIMEOUT = _DATA["element_timeout"]


@allure.feature("PC版官網儲值與購點")
@pytest.mark.usefixtures("class_driver")
class TestPCTopupStore:

    @pytest.fixture(autouse=True)
    def _inject(self, class_driver):
        self.driver = class_driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-001：開啟儲值與購點彈窗")
    def test_tc_pc_sp_001_open_topup_popup(self):
        # Test ID: TC-PC-SP-001
        # Test Title: 開啟儲值與購點彈窗
        # Test Steps:
        #   前置) 登入 beanfun 帳號
        #   1. 點擊 GASH 點數子選單中的「儲值與購點」
        #   2. 驗證儲值與購點彈窗已成功開啟（fbContent 存在）
        # Expected Result: 儲值與購點彈窗成功開啟，fbContent 元素可見

        with allure.step("前置：登入 beanfun 帳號"):
            account, password = require_beanfun_credentials()
            otp = get_beanfun_otp()
            self.home.go_to_home()
            self.home.click_login_btn()
            self.login.login_action(account, password)
            self.login.fill_otp_code(otp)
            self.login.click_final_confirm()
            WebDriverWait(self.driver, 20).until(
                EC.url_contains("beanfun.com")
            )
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()

        with allure.step("1. 驗證儲值與購點彈窗已成功開啟（fbContent 存在）"):
            self.home.open_topup_popup()
            self.topup.assert_popup_root_visible(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-002：儲值頁面帳號資訊驗證")
    def test_tc_pc_sp_002_account_info(self):
        # Test ID: TC-PC-SP-002
        # Test Title: 儲值頁面帳號資訊驗證
        # Test Steps:
        #   1. 於已開啟的儲值彈窗，切換至功能操作區域（iframe）
        #   2. 偵測並處理防詐騙 OTP 驗證彈窗（系統預期行為）
        #   3. 驗證左側帳號資訊區的「剩餘點數」數值可見，並截圖留存
        # Expected Result: 帳號資訊區「剩餘點數」可見

        with allure.step("1. 於已開啟的儲值彈窗，切換至功能操作區域"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)

        with allure.step("2. 偵測並處理防詐騙 OTP 驗證彈窗（系統預期行為）"):
            self.topup.dismiss_anti_fraud_if_present(timeout=5)

        with allure.step("3. 驗證左側帳號資訊區的「剩餘點數」數值可見，並截圖留存"):
            self.topup.assert_remaining_points_visible(_TIMEOUT)
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="剩餘點數截圖",
                attachment_type=allure.attachment_type.PNG,
            )

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-003：購買點數頁面驗證")
    def test_tc_pc_sp_003_buy_points_page(self):
        # Test ID: TC-PC-SP-003
        # Test Title: 購買點數頁面驗證
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「購買點數」選項
        #   2. 驗證「購買點數」頁面內容載入或項目存在於頁面
        # Expected Result: 「購買點數」頁面主要內容可見

        with allure.step("1. 在儲值頁面左側導覽列，點擊「購買點數」選項"):
            self.topup.click_nav_item(TopupPopupPage.NAV_BUY_POINTS)

        with allure.step("2. 驗證「購買點數」頁面內容載入或項目存在於頁面"):
            self.topup.assert_page_content_loaded(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-004：查詢記錄 - 儲值記錄")
    def test_tc_pc_sp_004_topup_record(self):
        # Test ID: TC-PC-SP-004
        # Test Title: 查詢記錄 - 儲值記錄
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「儲值記錄」選項
        #   2. 驗證「儲值記錄」頁面內容載入或項目存在於頁面
        # Expected Result: 「儲值記錄」頁面主要內容可見

        with allure.step("1. 在儲值頁面左側導覽列，點擊「儲值記錄」選項"):
            self.topup.click_nav_item(TopupPopupPage.NAV_TOPUP_RECORD)

        with allure.step("2. 驗證「儲值記錄」頁面內容載入或項目存在於頁面"):
            self.topup.assert_page_content_loaded(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-005
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-005：查詢記錄 - 消費記錄")
    def test_tc_pc_sp_005_consumption_record(self):
        # Test ID: TC-PC-SP-005
        # Test Title: 查詢記錄 - 消費記錄
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「消費記錄」選項
        #   2. 驗證「消費記錄」頁面內容載入或項目存在於頁面
        # Expected Result: 「消費記錄」頁面主要內容可見

        with allure.step("1. 在儲值頁面左側導覽列，點擊「消費記錄」選項"):
            self.topup.click_nav_item(TopupPopupPage.NAV_CONSUMPTION)

        with allure.step("2. 驗證「消費記錄」頁面內容載入或項目存在於頁面"):
            self.topup.assert_page_content_loaded(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-006
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-006：查詢記錄 - 遊戲專用點數")
    def test_tc_pc_sp_006_game_points(self):
        # Test ID: TC-PC-SP-006
        # Test Title: 查詢記錄 - 遊戲專用點數
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「遊戲專用點數」選項
        #   2. 驗證「遊戲專用點數」頁面內容載入或項目存在於頁面
        # Expected Result: 「遊戲專用點數」頁面主要內容可見

        with allure.step("1. 在儲值頁面左側導覽列，點擊「遊戲專用點數」選項"):
            self.topup.click_nav_item(TopupPopupPage.NAV_GAME_POINTS)

        with allure.step("2. 驗證「遊戲專用點數」頁面內容載入或項目存在於頁面"):
            self.topup.assert_page_content_loaded(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-007
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-007：查詢記錄 - 最近儲值記錄")
    def test_tc_pc_sp_007_recent_topup(self):
        # Test ID: TC-PC-SP-007
        # Test Title: 查詢記錄 - 最近儲值記錄
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「最近儲值記錄」選項
        #   2. 驗證「最近儲值記錄」頁面內容載入或項目存在於頁面
        # Expected Result: 「最近儲值記錄」頁面主要內容可見

        with allure.step("1. 在儲值頁面左側導覽列，點擊「最近儲值記錄」選項"):
            self.topup.click_nav_item(TopupPopupPage.NAV_RECENT_TOPUP)

        with allure.step("2. 驗證「最近儲值記錄」頁面內容載入或項目存在於頁面"):
            self.topup.assert_page_content_loaded(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-008
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-008：計費設定頁面")
    def test_tc_pc_sp_008_billing_settings(self):
        # Test ID: TC-PC-SP-008
        # Test Title: 計費設定頁面
        # Test Steps:
        #   1. 在儲值頁面左側導覽列，點擊「計費設定」選項
        #   2. 驗證「計費設定」頁面內容載入或項目存在於頁面
        # Expected Result: 「計費設定」頁面主要內容可見

        with allure.step("1. 在儲值頁面左側導覽列，點擊「計費設定」選項"):
            self.topup.click_nav_item(TopupPopupPage.NAV_BILLING)

        with allure.step("2. 驗證「計費設定」頁面內容載入或項目存在於頁面"):
            self.topup.assert_page_content_loaded(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-009
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-009：更新當前點數")
    def test_tc_pc_sp_009_current_points(self):
        # Test ID: TC-PC-SP-009
        # Test Title: 更新當前點數
        # Test Steps:
        #   1. 於已開啟的儲值彈窗，切換至功能操作區域
        #   2. 驗證左側帳號資訊區的「當前點數」數值可見，並截圖留存
        # Expected Result: 帳號資訊區「當前點數」可見

        with allure.step("1. 於已開啟的儲值彈窗，切換至功能操作區域"):
            self.topup.switch_to_popup_iframe(_TIMEOUT)

        with allure.step("2. 驗證左側帳號資訊區的「當前點數」數值可見，並截圖留存"):
            self.topup.assert_current_points_visible(_TIMEOUT)
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="當前點數截圖",
                attachment_type=allure.attachment_type.PNG,
            )

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-010
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-010：關閉儲值與購點彈窗")
    def test_tc_pc_sp_010_close_popup(self):
        # Test ID: TC-PC-SP-010
        # Test Title: 關閉儲值與購點彈窗
        # Test Steps:
        #   1. 點擊儲值彈窗右上角的「關閉」按鈕，並截圖留存
        # Expected Result: 儲值與購點彈窗成功關閉，fbContent 消失

        with allure.step("1. 點擊儲值彈窗右上角的「關閉」按鈕，並截圖留存"):
            self.topup.click_close_button(_TIMEOUT)
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="關閉彈窗後截圖",
                attachment_type=allure.attachment_type.PNG,
            )
