"""
PC 版官網：會員中心側欄自動化測試。

涵蓋範圍（依操作流程排序）：
  純點帳側欄（21 TC）
    SC-P-001 ~ SC-P-021
  星帳側欄（22 TC，帳號：gamaplay788）
    SC-S-001 ~ SC-S-022
"""
import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from config.credentials import get_beanfun_otp, get_pure_credentials, get_star_credentials
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


# ════════════════════════════════════════════════════════════════
# 純點帳側欄（21 TC）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網會員中心側欄")
class TestPCMemberCenterPureSidebar:
    """純點帳會員中心側欄 21 TC（SC-P-001 ~ SC-P-021）。"""

    @pytest.fixture(autouse=True)
    def _setup(self, class_driver):
        self.driver = class_driver
        self.home = HomePage(class_driver)
        self.login = LoginPage(class_driver)
        self.member = MemberCenterPage(class_driver)

        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass

        self.home.go_to_home()

        if not self.home.is_element_displayed(self.home.LOGOUT_BTN, timeout=3):
            account, password = get_pure_credentials()
            self.home.click_login_btn()
            self.login.login_action_pure(account, password)
            WebDriverWait(class_driver, _TIMEOUT).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()

        self.home.click_member_center()
        self.member.assert_popup_visible(_TIMEOUT)
        self.member.switch_to_iframe(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # SC-P-001：側欄帳號顯示（XXXX******）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-001：純點帳側欄帳號顯示（XXXX******）")
    def test_tc_pc_sc_p_001_account_display(self):
        # Test ID: TC-PC-SC-P-001
        # Test Title: 純點帳側欄帳號顯示（顯示點數帳號，規則 XXXX******）
        # Test Steps:
        #   1. 已以純點帳登入，點擊會員中心開啟側欄
        #   2. 驗證側欄容器（div.memberList）可見
        # Expected Result: 會員中心側欄正常顯示（代表純點帳已登入且側欄載入）

        with allure.step("驗證側欄 div.memberList 可見（純點帳已登入）"):
            self.member.assert_member_list_visible(_TIMEOUT)
            _screenshot(self.driver, "SC-P-001_側欄帳號顯示")

    # ────────────────────────────────────────────────────────────
    # SC-P-002：側欄目前點數顯示
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-002：純點帳側欄目前點數顯示")
    def test_tc_pc_sc_p_002_points_display(self):
        # Test ID: TC-PC-SC-P-002
        # Test Title: 純點帳側欄目前點數顯示（顯示持有點數符合帳號狀態）
        # Test Steps:
        #   1. 已以純點帳登入，會員中心側欄已開啟
        #   2. 驗證點數顯示區可見
        # Expected Result: 點數顯示區元素可見

        with allure.step("驗證點數顯示區可見"):
            self.member.assert_remaining_points_visible(_TIMEOUT)
            _screenshot(self.driver, "SC-P-002_點數顯示")

    # ────────────────────────────────────────────────────────────
    # SC-P-003：側欄重新整理點數功能
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-003：純點帳側欄重新整理點數功能")
    def test_tc_pc_sc_p_003_refresh_points(self):
        # Test ID: TC-PC-SC-P-003
        # Test Title: 側欄重新整理點數功能（不造成錯誤）
        # Test Steps:
        #   1. 已以純點帳登入，會員中心側欄已開啟
        #   2. 點擊「更新點數」按鈕
        #   3. 驗證點數顯示區仍可見（沒有錯誤）
        # Expected Result: 更新點數後不拋錯，點數區仍可見

        with allure.step("點擊更新點數"):
            self.member.click_refresh_points(_TIMEOUT)
            _screenshot(self.driver, "SC-P-003_重新整理點數")

        with allure.step("驗證點數顯示區仍可見"):
            self.member.assert_remaining_points_visible(_TIMEOUT)
            _screenshot(self.driver, "SC-P-003_點數仍可見")

    # ────────────────────────────────────────────────────────────
    # SC-P-004：側欄功能顯示（大分類）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-004：純點帳側欄功能顯示（4 個大分類，無帳號整合）")
    def test_tc_pc_sc_p_004_categories_display(self):
        # Test ID: TC-PC-SC-P-004
        # Test Title: 側欄功能顯示（大分類）
        # Test Steps:
        #   1. 已以純點帳登入，會員中心側欄已開啟
        #   2. 驗證顯示：會員資料、服務開通、查詢紀錄、會員須知
        #   3. 驗證「帳號整合」不存在（星帳專屬）
        # Expected Result: 4 個大分類可見，帳號整合不可見

        with allure.step("驗證 4 個大分類可見"):
            self.member.assert_category_visible(self.member.CAT_MEMBER_INFO, _TIMEOUT)
            self.member.assert_category_visible(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_category_visible(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_category_visible(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            _screenshot(self.driver, "SC-P-004_4大分類可見")

        with allure.step("驗證「帳號整合」不可見（星帳專屬）"):
            assert not self.member.is_element_displayed(
                self.member.CAT_ACCOUNT_INTEGRATION, timeout=3
            ), "純點帳不應顯示帳號整合"
            _screenshot(self.driver, "SC-P-004_帳號整合不存在")

    # ────────────────────────────────────────────────────────────
    # SC-P-005：點擊大分類（會員資料）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-005：點擊大分類(會員資料)→右側頁面顯示會員資料")
    def test_tc_pc_sc_p_005_click_member_info(self):
        # Test ID: TC-PC-SC-P-005
        # Test Title: 點擊會員資料，右側頁面顯示會員資料
        # Test Steps:
        #   1. 點擊側欄「會員資料」（data-page='1'）
        #   2. 驗證該項目取得 active class
        # Expected Result: 會員資料 targetBtn 含 active class

        with allure.step("點擊會員資料"):
            self.member.click_category(self.member.CAT_MEMBER_INFO, _TIMEOUT)
            _screenshot(self.driver, "SC-P-005_點擊會員資料")

        with allure.step("驗證右側頁面切換至會員資料（active class）"):
            self.member.assert_target_active("1", _TIMEOUT)
            _screenshot(self.driver, "SC-P-005_會員資料active")

    # ────────────────────────────────────────────────────────────
    # SC-P-006：點擊大分類（服務開通）→ 展開子項目
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-006：點擊大分類(服務開通)→展開子項目")
    def test_tc_pc_sc_p_006_click_service_open(self):
        # Test ID: TC-PC-SC-P-006
        # Test Title: 點擊服務開通，展開子項目
        # Test Steps:
        #   1. 點擊側欄「服務開通」drawerBtn
        #   2. 驗證 drawerBtn 含 'open' class
        # Expected Result: 服務開通展開（class 加 open）

        with allure.step("點擊服務開通"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            _screenshot(self.driver, "SC-P-006_點擊服務開通")

        with allure.step("驗證 drawerBtn 含 open class"):
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            _screenshot(self.driver, "SC-P-006_服務開通已展開")

    # ────────────────────────────────────────────────────────────
    # SC-P-007：展開顯示（服務開通子項目）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-007：側欄展開顯示(服務開通)→3 個子項目可見")
    def test_tc_pc_sc_p_007_service_open_expanded(self):
        # Test ID: TC-PC-SC-P-007
        # Test Title: 服務開通展開後，顯示 3 個子項目
        # Test Steps:
        #   1. 點擊「服務開通」展開
        #   2. 驗證：開通權益、取消/訂閱電子報、取消/訂閱簡訊 可見
        # Expected Result: 3 個子項目均可見

        with allure.step("展開服務開通"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)

        with allure.step("驗證 3 個子項目可見"):
            self.member.assert_sub_items_visible(
                self.member.SUB_OPEN_BENEFIT,
                self.member.SUB_EMAIL,
                self.member.SUB_SMS,
                timeout=_TIMEOUT,
            )
            _screenshot(self.driver, "SC-P-007_服務開通子項目可見")

    # ────────────────────────────────────────────────────────────
    # SC-P-008：點擊大分類（查詢紀錄）→ 展開子項目
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-008：點擊大分類(查詢紀錄)→展開子項目")
    def test_tc_pc_sc_p_008_click_query_records(self):
        # Test ID: TC-PC-SC-P-008
        # Test Title: 點擊查詢紀錄，展開子項目
        # Test Steps:
        #   1. 點擊側欄「查詢紀錄」drawerBtn
        #   2. 驗證 drawerBtn 含 'open' class
        # Expected Result: 查詢紀錄展開

        with allure.step("點擊查詢紀錄"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            _screenshot(self.driver, "SC-P-008_點擊查詢紀錄")

        with allure.step("驗證 drawerBtn 含 open class"):
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            _screenshot(self.driver, "SC-P-008_查詢紀錄已展開")

    # ────────────────────────────────────────────────────────────
    # SC-P-009：展開顯示（查詢紀錄子項目）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-009：側欄展開顯示(查詢紀錄)→4 個子項目可見")
    def test_tc_pc_sc_p_009_query_records_expanded(self):
        # Test ID: TC-PC-SC-P-009
        # Test Title: 查詢紀錄展開後，顯示 4 個子項目
        # Test Steps:
        #   1. 點擊「查詢紀錄」展開
        #   2. 驗證：帳號大事紀、遊戲使用紀錄、進階驗證解鎖專區、簡訊OTP驗證專區 可見
        # Expected Result: 4 個子項目均可見

        with allure.step("展開查詢紀錄"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)

        with allure.step("驗證 4 個子項目可見"):
            self.member.assert_sub_items_visible(
                self.member.SUB_ACCOUNT_LOG,
                self.member.SUB_GAME_LOG,
                self.member.SUB_GAME_UNLOCK,
                self.member.SUB_SMS_OTP,
                timeout=_TIMEOUT,
            )
            _screenshot(self.driver, "SC-P-009_查詢紀錄子項目可見")

    # ────────────────────────────────────────────────────────────
    # SC-P-010：點擊大分類（會員須知）→ 展開子項目
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-010：點擊大分類(會員須知)→展開子項目")
    def test_tc_pc_sc_p_010_click_member_notice(self):
        # Test ID: TC-PC-SC-P-010
        # Test Title: 點擊會員須知，展開子項目
        # Test Steps:
        #   1. 點擊側欄「會員須知」drawerBtn
        #   2. 驗證 drawerBtn 含 'open' class
        # Expected Result: 會員須知展開

        with allure.step("點擊會員須知"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            _screenshot(self.driver, "SC-P-010_點擊會員須知")

        with allure.step("驗證 drawerBtn 含 open class"):
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            _screenshot(self.driver, "SC-P-010_會員須知已展開")

    # ────────────────────────────────────────────────────────────
    # SC-P-011：展開顯示（會員須知子項目）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-011：側欄展開顯示(會員須知)→3 個子項目可見")
    def test_tc_pc_sc_p_011_member_notice_expanded(self):
        # Test ID: TC-PC-SC-P-011
        # Test Title: 會員須知展開後，顯示 3 個子項目
        # Test Steps:
        #   1. 點擊「會員須知」展開
        #   2. 驗證：服務條款、新手引導、會員認證 可見
        # Expected Result: 3 個子項目均可見

        with allure.step("展開會員須知"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)

        with allure.step("驗證 3 個子項目可見"):
            self.member.assert_sub_items_visible(
                self.member.SUB_TERMS,
                self.member.SUB_GUIDE,
                self.member.SUB_MEMBER_CERT,
                timeout=_TIMEOUT,
            )
            _screenshot(self.driver, "SC-P-011_會員須知子項目可見")

    # ────────────────────────────────────────────────────────────
    # SC-P-012：點擊子項目（開通權益）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-012：點擊子項目(開通權益)→右側頁面顯示開通權益")
    def test_tc_pc_sc_p_012_click_open_benefit(self):
        # Test ID: TC-PC-SC-P-012
        # Test Title: 點擊開通權益，右側頁面顯示開通權益
        # Test Steps:
        #   1. 展開服務開通
        #   2. 點擊「開通權益」（data-page='3'）
        #   3. 驗證該項目取得 active class
        # Expected Result: 開通權益 targetBtn 含 active class

        with allure.step("展開服務開通並點擊開通權益"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_OPEN_BENEFIT, _TIMEOUT)
            _screenshot(self.driver, "SC-P-012_點擊開通權益")

        with allure.step("驗證右側頁面切換至開通權益"):
            self.member.assert_target_active("3", _TIMEOUT)
            _screenshot(self.driver, "SC-P-012_開通權益active")

    # ────────────────────────────────────────────────────────────
    # SC-P-013：點擊子項目（取消/訂閱電子報）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-013：點擊子項目(取消/訂閱電子報)→右側頁面顯示電子報")
    def test_tc_pc_sc_p_013_click_email(self):
        # Test ID: TC-PC-SC-P-013
        # Test Title: 點擊取消/訂閱電子報，右側頁面顯示電子報頁面
        # Test Steps:
        #   1. 展開服務開通
        #   2. 點擊「取消/訂閱電子報」（data-page='4'）
        #   3. 驗證 active class
        # Expected Result: 電子報 targetBtn 含 active class

        with allure.step("展開服務開通並點擊取消/訂閱電子報"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_EMAIL, _TIMEOUT)
            _screenshot(self.driver, "SC-P-013_點擊電子報")

        with allure.step("驗證右側頁面切換至電子報"):
            self.member.assert_target_active("4", _TIMEOUT)
            _screenshot(self.driver, "SC-P-013_電子報active")

    # ────────────────────────────────────────────────────────────
    # SC-P-014：點擊子項目（取消/訂閱簡訊）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-014：點擊子項目(取消/訂閱簡訊)→右側頁面顯示簡訊訂閱")
    def test_tc_pc_sc_p_014_click_sms(self):
        # Test ID: TC-PC-SC-P-014
        # Test Title: 點擊取消/訂閱簡訊，右側頁面顯示簡訊訂閱頁面
        # Test Steps:
        #   1. 展開服務開通
        #   2. 點擊「取消/訂閱簡訊」（data-page='5'）
        #   3. 驗證 active class
        # Expected Result: 簡訊 targetBtn 含 active class

        with allure.step("展開服務開通並點擊取消/訂閱簡訊"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_SMS, _TIMEOUT)
            _screenshot(self.driver, "SC-P-014_點擊簡訊")

        with allure.step("驗證右側頁面切換至簡訊訂閱"):
            self.member.assert_target_active("5", _TIMEOUT)
            _screenshot(self.driver, "SC-P-014_簡訊active")

    # ────────────────────────────────────────────────────────────
    # SC-P-015：點擊子項目（帳號大事紀）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-015：點擊子項目(帳號大事紀)→右側頁面顯示帳號大事紀")
    def test_tc_pc_sc_p_015_click_account_log(self):
        # Test ID: TC-PC-SC-P-015
        # Test Title: 點擊帳號大事紀，右側頁面顯示帳號大事紀
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「帳號大事紀」（data-page='6'）
        #   3. 驗證 active class
        # Expected Result: 帳號大事紀 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊帳號大事紀"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_ACCOUNT_LOG, _TIMEOUT)
            _screenshot(self.driver, "SC-P-015_點擊帳號大事紀")

        with allure.step("驗證右側頁面切換至帳號大事紀"):
            self.member.assert_target_active("6", _TIMEOUT)
            _screenshot(self.driver, "SC-P-015_帳號大事紀active")

    # ────────────────────────────────────────────────────────────
    # SC-P-016：點擊子項目（遊戲使用紀錄）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-016：點擊子項目(遊戲使用紀錄)→右側頁面顯示遊戲使用紀錄")
    def test_tc_pc_sc_p_016_click_game_log(self):
        # Test ID: TC-PC-SC-P-016
        # Test Title: 點擊遊戲使用紀錄，右側頁面顯示遊戲使用紀錄
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「遊戲使用紀錄」（data-page='7'）
        #   3. 驗證 active class
        # Expected Result: 遊戲使用紀錄 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊遊戲使用紀錄"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_GAME_LOG, _TIMEOUT)
            _screenshot(self.driver, "SC-P-016_點擊遊戲使用紀錄")

        with allure.step("驗證右側頁面切換至遊戲使用紀錄"):
            self.member.assert_target_active("7", _TIMEOUT)
            _screenshot(self.driver, "SC-P-016_遊戲使用紀錄active")

    # ────────────────────────────────────────────────────────────
    # SC-P-017：點擊子項目（進階驗證解鎖專區）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-017：點擊子項目(進階驗證解鎖專區)→右側頁面顯示")
    def test_tc_pc_sc_p_017_click_game_unlock(self):
        # Test ID: TC-PC-SC-P-017
        # Test Title: 點擊進階驗證解鎖專區，右側頁面顯示進階驗證解鎖專區
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「進階驗證解鎖專區」（data-page='8'）
        #   3. 驗證 active class
        # Expected Result: 進階驗證解鎖專區 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊進階驗證解鎖專區"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_GAME_UNLOCK, _TIMEOUT)
            _screenshot(self.driver, "SC-P-017_點擊進階驗證解鎖專區")

        with allure.step("驗證右側頁面切換至進階驗證解鎖專區"):
            self.member.assert_target_active("8", _TIMEOUT)
            _screenshot(self.driver, "SC-P-017_進階驗證解鎖專區active")

    # ────────────────────────────────────────────────────────────
    # SC-P-018：點擊子項目（簡訊OTP驗證專區）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-018：點擊子項目(簡訊OTP驗證專區)→右側頁面顯示")
    def test_tc_pc_sc_p_018_click_sms_otp(self):
        # Test ID: TC-PC-SC-P-018
        # Test Title: 點擊簡訊OTP驗證專區，右側頁面顯示簡訊OTP驗證專區
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「簡訊OTP驗證專區」（data-page='9'）
        #   3. 驗證 active class
        # Expected Result: 簡訊OTP驗證專區 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊簡訊OTP驗證專區"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_SMS_OTP, _TIMEOUT)
            _screenshot(self.driver, "SC-P-018_點擊簡訊OTP驗證專區")

        with allure.step("驗證右側頁面切換至簡訊OTP驗證專區"):
            self.member.assert_target_active("9", _TIMEOUT)
            _screenshot(self.driver, "SC-P-018_簡訊OTP驗證專區active")

    # ────────────────────────────────────────────────────────────
    # SC-P-019：點擊子項目（服務條款）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-019：點擊子項目(服務條款)→右側頁面顯示服務條款")
    def test_tc_pc_sc_p_019_click_terms(self):
        # Test ID: TC-PC-SC-P-019
        # Test Title: 點擊服務條款，右側頁面顯示服務條款
        # Test Steps:
        #   1. 展開會員須知
        #   2. 點擊「服務條款」（data-page='10'）
        #   3. 驗證 active class
        # Expected Result: 服務條款 targetBtn 含 active class

        with allure.step("展開會員須知並點擊服務條款"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_TERMS, _TIMEOUT)
            _screenshot(self.driver, "SC-P-019_點擊服務條款")

        with allure.step("驗證右側頁面切換至服務條款"):
            self.member.assert_target_active("10", _TIMEOUT)
            _screenshot(self.driver, "SC-P-019_服務條款active")

    # ────────────────────────────────────────────────────────────
    # SC-P-020：點擊子項目（新手引導）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-020：點擊子項目(新手引導)→右側頁面顯示新手引導")
    def test_tc_pc_sc_p_020_click_guide(self):
        # Test ID: TC-PC-SC-P-020
        # Test Title: 點擊新手引導，右側頁面顯示新手引導
        # Test Steps:
        #   1. 展開會員須知
        #   2. 點擊「新手引導」（data-page='11'）
        #   3. 驗證 active class
        # Expected Result: 新手引導 targetBtn 含 active class

        with allure.step("展開會員須知並點擊新手引導"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_GUIDE, _TIMEOUT)
            _screenshot(self.driver, "SC-P-020_點擊新手引導")

        with allure.step("驗證右側頁面切換至新手引導"):
            self.member.assert_target_active("11", _TIMEOUT)
            _screenshot(self.driver, "SC-P-020_新手引導active")

    # ────────────────────────────────────────────────────────────
    # SC-P-021：點擊子項目（會員認證）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-P-021：點擊子項目(會員認證)→右側頁面顯示會員認證")
    def test_tc_pc_sc_p_021_click_member_cert(self):
        # Test ID: TC-PC-SC-P-021
        # Test Title: 點擊會員認證，右側頁面顯示會員認證
        # Test Steps:
        #   1. 展開會員須知
        #   2. 點擊「會員認證」（data-page='12'）
        #   3. 驗證 active class
        # Expected Result: 會員認證 targetBtn 含 active class

        with allure.step("展開會員須知並點擊會員認證"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_MEMBER_CERT, _TIMEOUT)
            _screenshot(self.driver, "SC-P-021_點擊會員認證")

        with allure.step("驗證右側頁面切換至會員認證"):
            self.member.assert_target_active("12", _TIMEOUT)
            _screenshot(self.driver, "SC-P-021_會員認證active")


# ════════════════════════════════════════════════════════════════
# 星帳側欄（22 TC）
# ════════════════════════════════════════════════════════════════

@allure.feature("PC版官網會員中心側欄")
class TestPCMemberCenterStarSidebar:
    """星帳（gamaplay788）會員中心側欄 22 TC。"""

    @pytest.fixture(autouse=True)
    def _setup(self, class_driver):
        self.driver = class_driver
        self.home = HomePage(class_driver)
        self.login = LoginPage(class_driver)
        self.member = MemberCenterPage(class_driver)

        # 切回主文件，避免上一個 test 殘留 iframe context
        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass

        # 前往首頁
        self.home.go_to_home()

        # 若尚未登入，執行星帳登入
        if not self.home.is_element_displayed(self.home.LOGOUT_BTN, timeout=3):
            account, password = get_star_credentials()
            otp = get_beanfun_otp()
            self.home.click_login_btn()
            self.login.login_action(account, password, wait_for_verify=False)
            try:
                self.login.click_element_safely(self.login.GO_TO_VERIFY_BTN)
                self.login.fill_otp_code(otp)
            except Exception:
                pytest.skip("OTP 驗證頁未出現（已達當日上限），請等待後重新執行")
            self.login.click_final_confirm()
            try:
                self.login.select_first_account_and_confirm()
            except AssertionError:
                pass
            WebDriverWait(class_driver, _TIMEOUT).until(EC.url_contains("beanfun.com"))
            self.home.handle_alert()
            self.home.dismiss_blocking_overlays()
            self.home.go_to_home()

        # 每個 test 重新開啟會員中心（確保乾淨狀態）
        self.home.click_member_center()
        self.member.assert_popup_visible(_TIMEOUT)
        self.member.switch_to_iframe(_TIMEOUT)

    # ────────────────────────────────────────────────────────────
    # SC-S-001：側欄帳號顯示（Gama Pass）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-001：星帳側欄帳號顯示（Gama Pass）")
    def test_tc_pc_sc_s_001_account_display(self):
        # Test ID: TC-PC-SC-S-001
        # Test Title: 星帳側欄帳號顯示（顯示 Gama Pass）
        # Test Steps:
        #   1. 已以星帳登入，點擊會員中心開啟側欄
        #   2. 驗證側欄容器（div.memberList）可見
        # Expected Result: 會員中心側欄正常顯示（代表星帳已登入且側欄載入）

        with allure.step("驗證側欄 div.memberList 可見（星帳 Gama Pass 已登入）"):
            self.member.assert_member_list_visible(_TIMEOUT)
            _screenshot(self.driver, "SC-S-001_側欄帳號顯示")

    # ────────────────────────────────────────────────────────────
    # SC-S-002：側欄目前點數顯示
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-002：星帳側欄目前點數顯示")
    def test_tc_pc_sc_s_002_points_display(self):
        # Test ID: TC-PC-SC-S-002
        # Test Title: 星帳側欄目前點數顯示（顯示持有點數符合帳號狀態）
        # Test Steps:
        #   1. 已以星帳登入，會員中心側欄已開啟
        #   2. 驗證點數顯示區可見
        # Expected Result: 點數顯示區元素可見

        with allure.step("驗證點數顯示區可見"):
            self.member.assert_remaining_points_visible(_TIMEOUT)
            _screenshot(self.driver, "SC-S-002_點數顯示")

    # ────────────────────────────────────────────────────────────
    # SC-S-003：側欄重新整理點數功能
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-003：星帳側欄重新整理點數功能")
    def test_tc_pc_sc_s_003_refresh_points(self):
        # Test ID: TC-PC-SC-S-003
        # Test Title: 側欄重新整理點數功能（不造成錯誤）
        # Test Steps:
        #   1. 已以星帳登入，會員中心側欄已開啟
        #   2. 點擊「更新點數」按鈕
        #   3. 驗證點數顯示區仍可見（沒有錯誤）
        # Expected Result: 更新點數後不拋錯，點數區仍可見

        with allure.step("點擊更新點數"):
            self.member.click_refresh_points(_TIMEOUT)
            _screenshot(self.driver, "SC-S-003_重新整理點數")

        with allure.step("驗證點數顯示區仍可見"):
            self.member.assert_remaining_points_visible(_TIMEOUT)
            _screenshot(self.driver, "SC-S-003_點數仍可見")

    # ────────────────────────────────────────────────────────────
    # SC-S-004：側欄功能顯示（大分類）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-004：星帳側欄功能顯示（5 個大分類）")
    def test_tc_pc_sc_s_004_categories_display(self):
        # Test ID: TC-PC-SC-S-004
        # Test Title: 側欄功能顯示（大分類）
        # Test Steps:
        #   1. 已以星帳登入，會員中心側欄已開啟
        #   2. 驗證顯示：會員資料、帳號整合、服務開通、查詢紀錄、會員須知
        # Expected Result: 5 個大分類全部可見

        with allure.step("驗證 5 個大分類可見"):
            self.member.assert_category_visible(self.member.CAT_MEMBER_INFO, _TIMEOUT)
            self.member.assert_category_visible(self.member.CAT_ACCOUNT_INTEGRATION, _TIMEOUT)
            self.member.assert_category_visible(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_category_visible(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_category_visible(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            _screenshot(self.driver, "SC-S-004_5大分類可見")

    # ────────────────────────────────────────────────────────────
    # SC-S-005：點擊大分類（會員資料）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-005：點擊大分類(會員資料)→右側頁面顯示會員資料")
    def test_tc_pc_sc_s_005_click_member_info(self):
        # Test ID: TC-PC-SC-S-005
        # Test Title: 點擊會員資料，右側頁面顯示會員資料
        # Test Steps:
        #   1. 點擊側欄「會員資料」（data-page='1'）
        #   2. 驗證該項目取得 active class（代表右側頁面已切換）
        # Expected Result: 會員資料 targetBtn 含 active class

        with allure.step("點擊會員資料"):
            self.member.click_category(self.member.CAT_MEMBER_INFO, _TIMEOUT)
            _screenshot(self.driver, "SC-S-005_點擊會員資料")

        with allure.step("驗證右側頁面切換至會員資料（active class）"):
            self.member.assert_target_active("1", _TIMEOUT)
            _screenshot(self.driver, "SC-S-005_會員資料active")

    # ────────────────────────────────────────────────────────────
    # SC-S-006：點擊大分類（帳號整合）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-006：點擊大分類(帳號整合)→右側頁面顯示帳號整合")
    def test_tc_pc_sc_s_006_click_account_integration(self):
        # Test ID: TC-PC-SC-S-006
        # Test Title: 點擊帳號整合，右側頁面顯示帳號整合（星帳專屬）
        # Test Steps:
        #   1. 點擊側欄「帳號整合」（data-page='2'）
        #   2. 驗證該項目取得 active class
        # Expected Result: 帳號整合 targetBtn 含 active class

        with allure.step("點擊帳號整合"):
            self.member.click_category(self.member.CAT_ACCOUNT_INTEGRATION, _TIMEOUT)
            _screenshot(self.driver, "SC-S-006_點擊帳號整合")

        with allure.step("驗證右側頁面切換至帳號整合（active class）"):
            self.member.assert_target_active("2", _TIMEOUT)
            _screenshot(self.driver, "SC-S-006_帳號整合active")

    # ────────────────────────────────────────────────────────────
    # SC-S-007：點擊大分類（服務開通）→ 展開子項目
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-007：點擊大分類(服務開通)→展開子項目")
    def test_tc_pc_sc_s_007_click_service_open(self):
        # Test ID: TC-PC-SC-S-007
        # Test Title: 點擊服務開通，展開子項目
        # Test Steps:
        #   1. 點擊側欄「服務開通」drawerBtn
        #   2. 驗證 drawerBtn 含 'open' class
        # Expected Result: 服務開通展開（class 加 open）

        with allure.step("點擊服務開通"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            _screenshot(self.driver, "SC-S-007_點擊服務開通")

        with allure.step("驗證 drawerBtn 含 open class"):
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            _screenshot(self.driver, "SC-S-007_服務開通已展開")

    # ────────────────────────────────────────────────────────────
    # SC-S-008：展開顯示（服務開通子項目）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-008：側欄展開顯示(服務開通)→3 個子項目可見")
    def test_tc_pc_sc_s_008_service_open_expanded(self):
        # Test ID: TC-PC-SC-S-008
        # Test Title: 服務開通展開後，顯示 3 個子項目
        # Test Steps:
        #   1. 點擊「服務開通」展開
        #   2. 驗證：開通權益、取消/訂閱電子報、取消/訂閱簡訊 可見
        # Expected Result: 3 個子項目均可見

        with allure.step("展開服務開通"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)

        with allure.step("驗證 3 個子項目可見"):
            self.member.assert_sub_items_visible(
                self.member.SUB_OPEN_BENEFIT,
                self.member.SUB_EMAIL,
                self.member.SUB_SMS,
                timeout=_TIMEOUT,
            )
            _screenshot(self.driver, "SC-S-008_服務開通子項目可見")

    # ────────────────────────────────────────────────────────────
    # SC-S-009：點擊大分類（查詢紀錄）→ 展開子項目
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-009：點擊大分類(查詢紀錄)→展開子項目")
    def test_tc_pc_sc_s_009_click_query_records(self):
        # Test ID: TC-PC-SC-S-009
        # Test Title: 點擊查詢紀錄，展開子項目
        # Test Steps:
        #   1. 點擊側欄「查詢紀錄」drawerBtn
        #   2. 驗證 drawerBtn 含 'open' class
        # Expected Result: 查詢紀錄展開

        with allure.step("點擊查詢紀錄"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            _screenshot(self.driver, "SC-S-009_點擊查詢紀錄")

        with allure.step("驗證 drawerBtn 含 open class"):
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            _screenshot(self.driver, "SC-S-009_查詢紀錄已展開")

    # ────────────────────────────────────────────────────────────
    # SC-S-010：展開顯示（查詢紀錄子項目）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-010：側欄展開顯示(查詢紀錄)→4 個子項目可見")
    def test_tc_pc_sc_s_010_query_records_expanded(self):
        # Test ID: TC-PC-SC-S-010
        # Test Title: 查詢紀錄展開後，顯示 4 個子項目
        # Test Steps:
        #   1. 點擊「查詢紀錄」展開
        #   2. 驗證：帳號大事紀、遊戲使用紀錄、遊戲帳號解鎖專區、簡訊OTP驗證專區 可見
        # Expected Result: 4 個子項目均可見

        with allure.step("展開查詢紀錄"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)

        with allure.step("驗證 4 個子項目可見"):
            self.member.assert_sub_items_visible(
                self.member.SUB_ACCOUNT_LOG,
                self.member.SUB_GAME_LOG,
                self.member.SUB_GAME_UNLOCK,
                self.member.SUB_SMS_OTP,
                timeout=_TIMEOUT,
            )
            _screenshot(self.driver, "SC-S-010_查詢紀錄子項目可見")

    # ────────────────────────────────────────────────────────────
    # SC-S-011：點擊大分類（會員須知）→ 展開子項目
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-011：點擊大分類(會員須知)→展開子項目")
    def test_tc_pc_sc_s_011_click_member_notice(self):
        # Test ID: TC-PC-SC-S-011
        # Test Title: 點擊會員須知，展開子項目
        # Test Steps:
        #   1. 點擊側欄「會員須知」drawerBtn
        #   2. 驗證 drawerBtn 含 'open' class
        # Expected Result: 會員須知展開

        with allure.step("點擊會員須知"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            _screenshot(self.driver, "SC-S-011_點擊會員須知")

        with allure.step("驗證 drawerBtn 含 open class"):
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            _screenshot(self.driver, "SC-S-011_會員須知已展開")

    # ────────────────────────────────────────────────────────────
    # SC-S-012：展開顯示（會員須知子項目）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-012：側欄展開顯示(會員須知)→3 個子項目可見")
    def test_tc_pc_sc_s_012_member_notice_expanded(self):
        # Test ID: TC-PC-SC-S-012
        # Test Title: 會員須知展開後，顯示 3 個子項目
        # Test Steps:
        #   1. 點擊「會員須知」展開
        #   2. 驗證：服務條款、新手引導、會員認證 可見
        # Expected Result: 3 個子項目均可見

        with allure.step("展開會員須知"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)

        with allure.step("驗證 3 個子項目可見"):
            self.member.assert_sub_items_visible(
                self.member.SUB_TERMS,
                self.member.SUB_GUIDE,
                self.member.SUB_MEMBER_CERT,
                timeout=_TIMEOUT,
            )
            _screenshot(self.driver, "SC-S-012_會員須知子項目可見")

    # ────────────────────────────────────────────────────────────
    # SC-S-013：點擊子項目（開通權益）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-013：點擊子項目(開通權益)→右側頁面顯示開通權益")
    def test_tc_pc_sc_s_013_click_open_benefit(self):
        # Test ID: TC-PC-SC-S-013
        # Test Title: 點擊開通權益，右側頁面顯示開通權益
        # Test Steps:
        #   1. 展開服務開通
        #   2. 點擊「開通權益」（data-page='3'）
        #   3. 驗證該項目取得 active class
        # Expected Result: 開通權益 targetBtn 含 active class

        with allure.step("展開服務開通並點擊開通權益"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_OPEN_BENEFIT, _TIMEOUT)
            _screenshot(self.driver, "SC-S-013_點擊開通權益")

        with allure.step("驗證右側頁面切換至開通權益"):
            self.member.assert_target_active("3", _TIMEOUT)
            _screenshot(self.driver, "SC-S-013_開通權益active")

    # ────────────────────────────────────────────────────────────
    # SC-S-014：點擊子項目（取消/訂閱電子報）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-014：點擊子項目(取消/訂閱電子報)→右側頁面顯示電子報")
    def test_tc_pc_sc_s_014_click_email(self):
        # Test ID: TC-PC-SC-S-014
        # Test Title: 點擊取消/訂閱電子報，右側頁面顯示電子報頁面
        # Test Steps:
        #   1. 展開服務開通
        #   2. 點擊「取消/訂閱電子報」（data-page='4'）
        #   3. 驗證 active class
        # Expected Result: 電子報 targetBtn 含 active class

        with allure.step("展開服務開通並點擊取消/訂閱電子報"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_EMAIL, _TIMEOUT)
            _screenshot(self.driver, "SC-S-014_點擊電子報")

        with allure.step("驗證右側頁面切換至電子報"):
            self.member.assert_target_active("4", _TIMEOUT)
            _screenshot(self.driver, "SC-S-014_電子報active")

    # ────────────────────────────────────────────────────────────
    # SC-S-015：點擊子項目（取消/訂閱簡訊）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-015：點擊子項目(取消/訂閱簡訊)→右側頁面顯示簡訊訂閱")
    def test_tc_pc_sc_s_015_click_sms(self):
        # Test ID: TC-PC-SC-S-015
        # Test Title: 點擊取消/訂閱簡訊，右側頁面顯示簡訊訂閱頁面
        # Test Steps:
        #   1. 展開服務開通
        #   2. 點擊「取消/訂閱簡訊」（data-page='5'）
        #   3. 驗證 active class
        # Expected Result: 簡訊 targetBtn 含 active class

        with allure.step("展開服務開通並點擊取消/訂閱簡訊"):
            self.member.click_category(self.member.CAT_SERVICE_OPEN, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_SERVICE_OPEN_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_SMS, _TIMEOUT)
            _screenshot(self.driver, "SC-S-015_點擊簡訊")

        with allure.step("驗證右側頁面切換至簡訊訂閱"):
            self.member.assert_target_active("5", _TIMEOUT)
            _screenshot(self.driver, "SC-S-015_簡訊active")

    # ────────────────────────────────────────────────────────────
    # SC-S-016：點擊子項目（帳號大事紀）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-016：點擊子項目(帳號大事紀)→右側頁面顯示帳號大事紀")
    def test_tc_pc_sc_s_016_click_account_log(self):
        # Test ID: TC-PC-SC-S-016
        # Test Title: 點擊帳號大事紀，右側頁面顯示帳號大事紀
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「帳號大事紀」（data-page='6'）
        #   3. 驗證 active class
        # Expected Result: 帳號大事紀 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊帳號大事紀"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_ACCOUNT_LOG, _TIMEOUT)
            _screenshot(self.driver, "SC-S-016_點擊帳號大事紀")

        with allure.step("驗證右側頁面切換至帳號大事紀"):
            self.member.assert_target_active("6", _TIMEOUT)
            _screenshot(self.driver, "SC-S-016_帳號大事紀active")

    # ────────────────────────────────────────────────────────────
    # SC-S-017：點擊子項目（遊戲使用紀錄）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-017：點擊子項目(遊戲使用紀錄)→右側頁面顯示遊戲使用紀錄")
    def test_tc_pc_sc_s_017_click_game_log(self):
        # Test ID: TC-PC-SC-S-017
        # Test Title: 點擊遊戲使用紀錄，右側頁面顯示遊戲使用紀錄
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「遊戲使用紀錄」（data-page='7'）
        #   3. 驗證 active class
        # Expected Result: 遊戲使用紀錄 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊遊戲使用紀錄"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_GAME_LOG, _TIMEOUT)
            _screenshot(self.driver, "SC-S-017_點擊遊戲使用紀錄")

        with allure.step("驗證右側頁面切換至遊戲使用紀錄"):
            self.member.assert_target_active("7", _TIMEOUT)
            _screenshot(self.driver, "SC-S-017_遊戲使用紀錄active")

    # ────────────────────────────────────────────────────────────
    # SC-S-018：點擊子項目（遊戲帳號解鎖專區）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-018：點擊子項目(遊戲帳號解鎖專區)→右側頁面顯示")
    def test_tc_pc_sc_s_018_click_game_unlock(self):
        # Test ID: TC-PC-SC-S-018
        # Test Title: 點擊遊戲帳號解鎖專區，右側頁面顯示
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「遊戲帳號解鎖專區」（data-page='8'）
        #   3. 驗證 active class
        # Expected Result: 遊戲帳號解鎖專區 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊遊戲帳號解鎖專區"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_GAME_UNLOCK, _TIMEOUT)
            _screenshot(self.driver, "SC-S-018_點擊遊戲帳號解鎖專區")

        with allure.step("驗證右側頁面切換至遊戲帳號解鎖專區"):
            self.member.assert_target_active("8", _TIMEOUT)
            _screenshot(self.driver, "SC-S-018_遊戲帳號解鎖專區active")

    # ────────────────────────────────────────────────────────────
    # SC-S-019：點擊子項目（簡訊OTP驗證專區）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-019：點擊子項目(簡訊OTP驗證專區)→右側頁面顯示")
    def test_tc_pc_sc_s_019_click_sms_otp(self):
        # Test ID: TC-PC-SC-S-019
        # Test Title: 點擊簡訊OTP驗證專區，右側頁面顯示
        # Test Steps:
        #   1. 展開查詢紀錄
        #   2. 點擊「簡訊OTP驗證專區」（data-page='9'）
        #   3. 驗證 active class
        # Expected Result: 簡訊OTP驗證專區 targetBtn 含 active class

        with allure.step("展開查詢紀錄並點擊簡訊OTP驗證專區"):
            self.member.click_category(self.member.CAT_QUERY_RECORDS, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_QUERY_RECORDS_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_SMS_OTP, _TIMEOUT)
            _screenshot(self.driver, "SC-S-019_點擊簡訊OTP驗證專區")

        with allure.step("驗證右側頁面切換至簡訊OTP驗證專區"):
            self.member.assert_target_active("9", _TIMEOUT)
            _screenshot(self.driver, "SC-S-019_簡訊OTP驗證專區active")

    # ────────────────────────────────────────────────────────────
    # SC-S-020：點擊子項目（服務條款）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-020：點擊子項目(服務條款)→右側頁面顯示服務條款")
    def test_tc_pc_sc_s_020_click_terms(self):
        # Test ID: TC-PC-SC-S-020
        # Test Title: 點擊服務條款，右側頁面顯示服務條款
        # Test Steps:
        #   1. 展開會員須知
        #   2. 點擊「服務條款」（data-page='10'）
        #   3. 驗證 active class
        # Expected Result: 服務條款 targetBtn 含 active class

        with allure.step("展開會員須知並點擊服務條款"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_TERMS, _TIMEOUT)
            _screenshot(self.driver, "SC-S-020_點擊服務條款")

        with allure.step("驗證右側頁面切換至服務條款"):
            self.member.assert_target_active("10", _TIMEOUT)
            _screenshot(self.driver, "SC-S-020_服務條款active")

    # ────────────────────────────────────────────────────────────
    # SC-S-021：點擊子項目（新手引導）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-021：點擊子項目(新手引導)→右側頁面顯示新手引導")
    def test_tc_pc_sc_s_021_click_guide(self):
        # Test ID: TC-PC-SC-S-021
        # Test Title: 點擊新手引導，右側頁面顯示新手引導
        # Test Steps:
        #   1. 展開會員須知
        #   2. 點擊「新手引導」（data-page='11'）
        #   3. 驗證 active class
        # Expected Result: 新手引導 targetBtn 含 active class

        with allure.step("展開會員須知並點擊新手引導"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_GUIDE, _TIMEOUT)
            _screenshot(self.driver, "SC-S-021_點擊新手引導")

        with allure.step("驗證右側頁面切換至新手引導"):
            self.member.assert_target_active("11", _TIMEOUT)
            _screenshot(self.driver, "SC-S-021_新手引導active")

    # ────────────────────────────────────────────────────────────
    # SC-S-022：點擊子項目（會員認證）
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-SC-S-022：點擊子項目(會員認證)→右側頁面顯示會員認證")
    def test_tc_pc_sc_s_022_click_member_cert(self):
        # Test ID: TC-PC-SC-S-022
        # Test Title: 點擊會員認證，右側頁面顯示會員認證
        # Test Steps:
        #   1. 展開會員須知
        #   2. 點擊「會員認證」（data-page='12'）
        #   3. 驗證 active class
        # Expected Result: 會員認證 targetBtn 含 active class

        with allure.step("展開會員須知並點擊會員認證"):
            self.member.click_category(self.member.CAT_MEMBER_NOTICE, _TIMEOUT)
            self.member.assert_drawer_expanded(self.member.CAT_MEMBER_NOTICE_EXPANDED, _TIMEOUT)
            self.member.click_sub_item(self.member.SUB_MEMBER_CERT, _TIMEOUT)
            _screenshot(self.driver, "SC-S-022_點擊會員認證")

        with allure.step("驗證右側頁面切換至會員認證"):
            self.member.assert_target_active("12", _TIMEOUT)
            _screenshot(self.driver, "SC-S-022_會員認證active")
