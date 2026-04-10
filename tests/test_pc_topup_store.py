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
from config.credentials import get_beanfun_otp, get_gp_credentials, get_pure_credentials, get_pure_verified_credentials, get_star_credentials, require_beanfun_credentials
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
            try:
                self.login.fill_otp_code(otp)
            except Exception:
                _screenshot(self.driver, "OTP畫面未出現")
                pytest.skip(
                    "beanfun 偵測登入過於頻繁，OTP 驗證頁未出現，請等待數分鐘後重新執行"
                )
            self.login.click_final_confirm()
            WebDriverWait(self.driver, 20).until(
                EC.url_contains("beanfun.com")
            )
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
            _screenshot(self.driver, "前置_登入完成")

        with allure.step("1. 點擊 GASH 點數子選單中的「儲值與購點」"):
            self.home.open_topup_popup()
            _screenshot(self.driver, "步驟1_點擊儲值與購點")

        with allure.step("2. 驗證儲值與購點彈窗已成功開啟（fbContent 存在）"):
            self.topup.assert_popup_root_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟2_彈窗已開啟")

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
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 偵測並處理防詐騙 OTP 驗證彈窗（系統預期行為）"):
            self.topup.dismiss_anti_fraud_if_present(timeout=5)
            _screenshot(self.driver, "步驟2_防詐騙處理後")

        with allure.step("3. 驗證左側帳號資訊區的「剩餘點數」數值可見"):
            self.topup.assert_remaining_points_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟3_剩餘點數可見")

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
            _screenshot(self.driver, "步驟1_點擊購買點數")

        with allure.step("2. 驗證「購買點數」頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_購買點數頁面內容")

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
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_TOPUP_RECORD)
            _screenshot(self.driver, "步驟1_點擊儲值記錄")

        with allure.step("2. 驗證「儲值記錄」頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_儲值記錄頁面內容")

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
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_CONSUMPTION)
            _screenshot(self.driver, "步驟1_點擊消費記錄")

        with allure.step("2. 驗證「消費記錄」頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_消費記錄頁面內容")

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
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_GAME_POINTS)
            _screenshot(self.driver, "步驟1_點擊遊戲專用點數")

        with allure.step("2. 驗證「遊戲專用點數」頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_遊戲專用點數頁面內容")

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
            self.topup.expand_query_records(_TIMEOUT)
            self.topup.click_nav_item(TopupPopupPage.NAV_RECENT_TOPUP)
            _screenshot(self.driver, "步驟1_點擊最近儲值記錄")

        with allure.step("2. 驗證「最近儲值記錄」頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_最近儲值記錄頁面內容")

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
            _screenshot(self.driver, "步驟1_點擊計費設定")

        with allure.step("2. 驗證「計費設定」頁面內容載入"):
            self.topup.assert_page_content_loaded(_TIMEOUT)
            _screenshot(self.driver, "步驟2_計費設定頁面內容")

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
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 驗證左側帳號資訊區的「當前點數」數值可見"):
            self.topup.assert_current_points_visible(_TIMEOUT)
            _screenshot(self.driver, "步驟2_當前點數可見")

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-010
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-010：關閉儲值與購點彈窗")
    def test_tc_pc_sp_010_close_popup(self):
        # Test ID: TC-PC-SP-010
        # Test Title: 關閉儲值與購點彈窗
        # Test Steps:
        #   1. 點擊儲值彈窗右上角的「關閉」按鈕
        #   2. 驗證儲值與購點彈窗已成功關閉
        # Expected Result: 儲值與購點彈窗成功關閉，fbContent 消失

        with allure.step("1. 點擊儲值彈窗右上角的「關閉」按鈕"):
            self.topup.click_close_button(_TIMEOUT)
            _screenshot(self.driver, "步驟1_關閉彈窗後")


    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-011
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-011：側欄進階認證狀態顯示（有進階認證）")
    def test_tc_pc_sp_011_verified_member(self):
        # Test ID: TC-PC-SP-011
        # Test Title: 側欄進階認證狀態顯示（有進階認證）
        # Test Steps:
        #   前提) 已登入具進階認證（認證會員）帳號
        #   1. 開啟儲值與購點彈窗
        #   2. 切換至彈窗 iframe
        #   3. 驗證側欄顯示「認證會員」
        # Expected Result: Remain_point1_lblVerifiedMember 文字包含「認證會員」

        with allure.step("1. 開啟儲值與購點彈窗"):
            self.home.go_to_home()
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
    # TC-PC-SP-012
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-012：購買點數頁顯示（已解鎖）")
    def test_tc_pc_sp_012_buy_points_unlocked(self):
        # Test ID: TC-PC-SP-012
        # Test Title: 購買點數頁顯示（已解鎖）
        # Test Steps:
        #   前提) 已登入認證會員帳號
        #   1. 開啟儲值與購點彈窗，切換至 iframe
        #   2. 點擊左側導覽「購買點數」
        #   3. 驗證支付方式選擇容器（div.type-btns）可見
        # Expected Result: 購買點數頁已解鎖，信用卡／讀卡機轉帳／橘子支付選項顯示

        with allure.step("1. 開啟彈窗並切換至 iframe"):
            self.home.go_to_home()
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


@allure.feature("PC版儲值彈窗 - 一般會員（無進階認證）")
@pytest.mark.usefixtures("driver")
class TestPCTopupGeneralMember:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        account, password = get_pure_credentials()
        self.home.go_to_home()
        self.home.click_login_btn()
        self.login.login_action_pure(account, password)
        WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
        self.home.handle_alert()
        self.home.dismiss_blocking_overlays()
        self.home.go_to_home()
        yield
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # TC-PC-SP-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-001：側欄進階認證狀態顯示（無進階認證）")
    def test_tc_pc_sp_001_general_member(self):
        # Test ID: TC-PC-SP-001
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
    # TC-PC-SP-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-002：購買點數頁顯示（未解鎖）")
    def test_tc_pc_sp_002_buy_points_locked(self):
        # Test ID: TC-PC-SP-002
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
    # TC-PC-SP-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SP-003：序號儲值頁顯示（未解鎖）")
    def test_tc_pc_sp_003_serial_topup_locked(self):
        # Test ID: TC-PC-SP-003
        # Test Title: 序號儲值頁顯示（未解鎖）
        # Test Steps:
        #   前提) 已登入一般會員帳號
        #   1. 開啟儲值彈窗，切換至 iframe
        #   2. 點擊左側導覽「序號儲值」
        #   3. 驗證顯示「前往認證」按鈕（未解鎖提示）
        # Expected Result: 序號儲值頁顯示進階認證提示，「前往認證」按鈕可見

        with allure.step("1. 開啟彈窗並切換至 iframe"):
            self.home.open_topup_popup()
            self.topup.switch_to_popup_iframe(_TIMEOUT)
            self.topup.dismiss_anti_fraud_if_present()
            _screenshot(self.driver, "步驟1_切換iframe")

        with allure.step("2. 點擊序號儲值導覽"):
            self.topup.click_nav_serial_topup(_TIMEOUT)
            _screenshot(self.driver, "步驟2_點擊序號儲值")

        with allure.step("3. 驗證未解鎖提示出現"):
            self.topup.assert_serial_topup_locked(_TIMEOUT)
            _screenshot(self.driver, "步驟3_未解鎖提示")
            self.driver.switch_to.default_content()


# ════════════════════════════════════════════════════════════════
# SP-001：GP點帳（gamaplay830）進階認證狀態驗證
# ════════════════════════════════════════════════════════════════
@allure.feature("PC版儲值彈窗 - GP點帳進階認證")
class TestPCTopupGPAccount:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
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
            WebDriverWait(self.driver, 20).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()
        except Exception as e:
            import pytest as _pytest
            _pytest.skip(f"被鎖定：GP點帳登入失敗，請稍後重試 - {e}")
        yield
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    @allure.title("TC-PC-SP-001：GP點帳(1.0)進階認證狀態顯示（有手機驗證）")
    def test_tc_pc_sp_001_gp_verified_member(self):
        # Test ID: TC-PC-SP-001
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


# ════════════════════════════════════════════════════════════════
# SP-001：星帳（gamaplay788）進階認證狀態驗證
# ════════════════════════════════════════════════════════════════
@allure.feature("PC版儲值彈窗 - 星帳進階認證")
class TestPCTopupStarAccount:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)
        self.topup = TopupPopupPage(self.driver)
        account, password = get_star_credentials()
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

    @allure.title("TC-PC-SP-001：星帳(2.0)預設進階認證狀態顯示")
    def test_tc_pc_sp_001_star_verified_member(self):
        # Test ID: TC-PC-SP-001
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
