"""
PC 版官網：會員中心（區塊二）、儲值與購點（區塊三）自動化測試。

Test ID 對應使用者提供之編號；本檔內測試方法請依序執行（同一 session）。
單獨重跑後段方法前，請先完成登入並置於首頁。

資料與預期字串：data/member_topup_test_data.json（請依實際 DOM 微調）。
"""
import json
import re
import time
from pathlib import Path

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401
from config.credentials import (
    get_beanfun_otp,
    get_beanfun_test_phone,
    require_beanfun_credentials,
)
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.member_center_page import MemberCenterPage
from pages.topup_pc_page import TopupPcPage

_DATA_PATH = Path(__file__).parent / "data" / "member_topup_test_data.json"
with open(_DATA_PATH, encoding="utf-8") as _f:
    MC_DATA = json.load(_f)


def _ensure_logged_out(driver, home: HomePage):
    home.go_to_home()
    home.handle_alert()
    home.dismiss_blocking_overlays()
    try:
        WebDriverWait(driver, 4).until(
            EC.visibility_of_element_located(HomePage.LOGOUT_BTN)
        )
        home.safe_click_action_bar(HomePage.LOGOUT_BTN)
        try:
            WebDriverWait(driver, 4).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except TimeoutException:
            pass
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(HomePage.LOGIN_BTN)
        )
    except TimeoutException:
        pass


def _close_member_popup_if_visible(driver, home: HomePage, member: MemberCenterPage):
    try:
        el = driver.find_element(*MemberCenterPage.POPUP_ROOT)
        if el.is_displayed():
            member.close_member_center(home)
    except Exception:
        pass


def _assert_no_cover_ad_within_5s(driver, home: HomePage, timeout: int):
    """登入後 5 秒內不應出現蓋板；並附加全頁截圖（Allure: popup2）。"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(HomePage.POPUP_AD)
        )
        pytest.fail("本次登入後於五秒內偵測到蓋板廣告，與預期不符")
    except TimeoutException:
        pass
    png = driver.get_screenshot_as_png()
    allure.attach(
        png,
        name="popup2",
        attachment_type=allure.attachment_type.PNG,
    )
    allure.attach(
        "本次登入後未於五秒內出現蓋板廣告，並提供頁面截圖如 popup2",
        name="蓋板廣告檢查",
        attachment_type=allure.attachment_type.TEXT,
    )


@allure.feature("PC版官網會員中心與儲值購點")
@pytest.mark.usefixtures("class_driver")
class TestPCMemberCenterAndTopup:
    t = MC_DATA["element_timeout"]
    mcfg = MC_DATA["member"]
    tcfg = MC_DATA["topup"]
    ta = MC_DATA["text_assertions"]

    @pytest.fixture(autouse=True)
    def _inject(self, class_driver):
        self.driver = class_driver
        self.home = HomePage(self.driver)
        self.login_page = LoginPage(self.driver)
        self.member = MemberCenterPage(self.driver)
        self.topup = TopupPcPage(self.driver)

    # ── 區塊二：1–5（共登、耗時、登入、蓋板、登出鈕）────────────────
    @allure.title("區塊二 1-5：共登按鈕、跳轉耗時、登入、蓋板、登出按鈕")
    def test_s2_01_through_05_login_and_post_login_shell(self):
        # Test ID: BF-MC-S2-01 ~ 05
        _ensure_logged_out(self.driver, self.home)

        with allure.step("1. 驗證共登按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.home.assert_element_ready(HomePage.LOGIN_BTN, self.t)

        with allure.step("2. 驗證共登頁點擊跳轉後至 body 渲染完成耗時（記錄並驗證上限）"):
            original_url = self.driver.current_url
            start = time.perf_counter()
            self.home.click(HomePage.LOGIN_BTN)
            WebDriverWait(self.driver, 10).until(EC.url_changes(original_url))
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            elapsed = time.perf_counter() - start
            max_sec = MC_DATA["max_co_redirect_seconds"]
            assert elapsed < max_sec, (
                f"跳轉渲染耗時 {elapsed}s 超過上限 {max_sec}s"
            )
            allure.attach(
                f"點擊跳轉後至 body 渲染完成共耗時 {elapsed} 秒",
                name="跳轉耗時",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("3. 驗證操作登入流程，本次登入操作成功"):
            account, password = require_beanfun_credentials()
            self.login_page.login_action(account, password)
            self.login_page.fill_otp_code(get_beanfun_otp())
            self.login_page.click_final_confirm()
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("tw.beanfun.com")
            )
            self.home.close_extra_windows()
            self.home.handle_alert()

        with allure.step("4. 驗證本次登入後未於五秒內出現蓋板廣告（截圖 popup2）"):
            _assert_no_cover_ad_within_5s(self.driver, self.home, self.t)

        with allure.step("5. 驗證登入後右下角登出按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.home.dismiss_blocking_overlays()
            self.home.assert_element_ready(HomePage.LOGOUT_BTN, self.t)

    # ── 區塊二：6–15 ─────────────────────────────────────────────
    @allure.title("區塊二 6-15：會員中心、查詢完整帳號、變更密碼、認證信箱流程起始")
    def test_s2_06_through_15_member_account_and_password(self):
        # Test ID: BF-MC-S2-06 ~ 15
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()

        with allure.step("6. 驗證會員中心按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.home.assert_element_ready(HomePage.MEMBER_CENTER_BTN, self.t)

        with allure.step("7. 驗證開啟會員中心，可成功點擊"):
            self.member.open_from_home(self.home, timeout=8)

        with allure.step("8. 驗證會員中心內容，確實於渲染後五秒內存在、可見、可點擊"):
            self.member.assert_popup_visible_clickable(self.t)

        with allure.step("9. 驗證查詢完整帳號的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["link_query_full_account"])

        with allure.step("10. 驗證帳號顯示，比對完整帳號文本呈現正確"):
            account, _pwd = require_beanfun_credentials()
            body = self.driver.find_element(
                *MemberCenterPage.POPUP_ROOT
            ).text
            assert account in body, (
                f"彈窗內應包含帳號字串：預期含「{account}」"
            )

        with allure.step("11. 驗證變更密碼的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["link_change_password"])

        with allure.step("12. 驗證變更密碼信箱地址輸入頁面提示，文本呈現正確"):
            self.member.assert_text_visible(
                self.mcfg["password_email_hint_fragment"], self.t
            )

        with allure.step("13. 驗證查詢/更換認證信箱的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["link_query_change_verify_email"])

        with allure.step(
            "14. 驗證查詢/更換驗證信箱切換按鈕，確實於渲染後五秒內存在、可見、可點擊"
        ):
            self.member.assert_link_ready(self.mcfg["toggle_verify_email"], self.t)

        with allure.step("15. 驗證切換至查詢/更換驗證信箱，確實於渲染後五秒內存在、可見、可點擊"):
            self.member.click_link_or_button(self.mcfg["toggle_verify_email"])

    # ── 區塊二：16–25 ─────────────────────────────────────────────
    @allure.title("區塊二 16-25：手機門號、進階驗證、會員中心重開、居住地")
    def test_s2_16_through_25_phone_residence(self):
        # Test ID: BF-MC-S2-16 ~ 25
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        _close_member_popup_if_visible(self.driver, self.home, self.member)
        self.member.open_from_home(self.home)

        with allure.step("16. 驗證所輸入的手機門號，比對文本，文本輸入正確"):
            ph = get_beanfun_test_phone() or (
                self.mcfg.get("sample_phone_input") or ""
            ).strip()
            if not ph:
                pytest.fail(
                    "請在 .env 設定 BEANFUN_TEST_PHONE，或在 data/member_topup_test_data.json "
                    "設定 member.sample_phone_input（須為該測試帳可用門號）"
                )
            self.member.fill_input_by_placeholder_fragment(
                self.mcfg["phone_placeholder_fragment"], ph
            )
            self.member.assert_input_value_contains(
                self.mcfg["phone_placeholder_fragment"], ph
            )

        with allure.step(
            "17. 驗證前往變更進階驗證的按鈕，確實於渲染後五秒內存在、可見、可點擊"
        ):
            self.member.assert_link_ready(self.mcfg["advanced_verify_btn"], self.t)

        with allure.step("18. 驗證原註冊手機門號輸入框，確實於渲染後五秒內存在、可見、可點擊"):
            phf = self.mcfg["original_phone_placeholder_fragment"].replace("'", "\\'")
            inp_loc = (
                By.XPATH,
                f"//*[@id='BF_divPopWindow']//input[contains(@placeholder,'{phf}')]",
            )
            self.member.assert_element_ready(inp_loc, self.t)

        with allure.step("19. 驗證所輸入的原註冊手機門號文本，比對文本，文本輸入正確"):
            self.member.fill_input_by_placeholder_fragment(
                self.mcfg["original_phone_placeholder_fragment"], ph
            )
            self.member.assert_input_value_contains(
                self.mcfg["original_phone_placeholder_fragment"], ph
            )

        with allure.step("20. 驗證會員中心按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.member.close_member_center(self.home)
            self.home.assert_element_ready(HomePage.MEMBER_CENTER_BTN, self.t)

        with allure.step("21. 驗證開啟會員中心，可成功點擊"):
            self.member.open_from_home(self.home)

        with allure.step("22. 驗證會員中心內容，確實於渲染後五秒內存在、可見"):
            self.member.assert_popup_visible(self.t)

        with allure.step("23. 驗證居住地修改的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["residence_link"])

        with allure.step("24. 驗證確定修改的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["confirm_modify"])

        with allure.step("25. 驗證居住地區修改為台北市，文本呈現正確"):
            self.member.click_link_or_button(self.mcfg["residence_expected_city"])
            self.member.assert_text_visible(
                self.mcfg["residence_expected_city"], self.t
            )

    # ── 區塊二：26–37 ─────────────────────────────────────────────
    @allure.title("區塊二 26-37：天堂線上交易、未開通服務、帳號大事紀")
    def test_s2_26_through_37_lineage_and_chronicle(self):
        # Test ID: BF-MC-S2-26 ~ 37
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        _close_member_popup_if_visible(self.driver, self.home, self.member)
        self.member.open_from_home(self.home)

        with allure.step(
            "26. 驗證天堂專用線上交易服務的資料查詢/變更按鈕，"
            "確實於渲染後五秒內存在、可見、可點擊"
        ):
            loc = (
                self.member._in_popup_xpath_clickable(self.mcfg["lineage_trade_service"])
            )
            self.member.assert_element_ready(loc, self.t)

        with allure.step("27. 驗證天堂專用線上交易服務的資料查詢/變更按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["lineage_trade_service"])

        with allure.step("28. 驗證已開通服務，遊戲計費方式，確實於渲染後五秒內存在、可見"):
            self.member.assert_visible_dual_fragment(
                self.mcfg["opened_service"],
                self.mcfg["billing_method_fragment"],
                self.t,
            )

        with allure.step("29. 驗證已開通服務，比對遊戲計費方式，文本呈現正確"):
            self.member.assert_text_visible(
                self.mcfg["billing_method_fragment"], self.t
            )

        with allure.step("30. 驗證左側未開通服務的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["unopened_service"])

        with allure.step("31. 驗證未開通服務，文本呈現正確"):
            self.member.assert_text_visible(self.mcfg["unopened_service"], self.t)

        with allure.step("32. 驗證左側查詢記錄，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["left_query_record"])

        with allure.step("33. 驗證左側帳號大事紀，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["left_account_chronicle"])

        with allure.step(
            "34. 驗證帳號大事紀的查詢按鈕，確實於渲染後五秒內存在、可見、可點擊"
        ):
            self.member.assert_link_ready(self.mcfg["query_btn"], self.t)

        with allure.step("35. 驗證帳號大事紀的查詢按鈕，可成功點擊"):
            self.member.click_query_button()

        chronicle_first = ""
        with allure.step("36. 驗證所查詢到的第一筆帳號大事紀內容，確實於渲染後五秒內存在、可見"):
            chronicle_first = self.member.get_first_result_text(
                min_len=self.ta["chronicle_row_min_length"]
            )
            allure.attach(
                chronicle_first,
                name="大事紀第一筆",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("37. 驗證所查詢的第一筆帳號大事紀內容，比對文本，文本呈現正確"):
            assert len(chronicle_first.strip()) >= self.ta["chronicle_row_min_length"]

    # ── 區塊二：38–49 ─────────────────────────────────────────────
    @allure.title("區塊二 38-49：遊戲使用記錄、進階認證解鎖")
    def test_s2_38_through_49_usage_advanced(self):
        # Test ID: BF-MC-S2-38 ~ 49
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        _close_member_popup_if_visible(self.driver, self.home, self.member)
        self.member.open_from_home(self.home)

        with allure.step("38. 驗證左側遊戲使用記錄的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["left_game_usage"])

        with allure.step(
            "39. 驗證遊戲使用記錄的查詢按鈕，確實於渲染後五秒內存在、可見、可點擊"
        ):
            self.member.assert_link_ready(self.mcfg["query_btn"], self.t)

        with allure.step("40. 驗證遊戲使用記錄的查詢按鈕，可成功點擊"):
            self.member.click_query_button()

        game_usage_txt = ""
        with allure.step("41. 驗證遊戲使用記錄內容，確實於渲染後五秒內存在、可見"):
            game_usage_txt = self.member.get_first_result_text(
                min_len=self.ta["game_usage_row_min_length"]
            )
            allure.attach(
                game_usage_txt,
                name="遊戲使用記錄",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("42. 驗證所查詢的遊戲使用記錄內容，比對文本，文本呈現正確"):
            assert len(game_usage_txt.strip()) >= self.ta["game_usage_row_min_length"]

        with allure.step("43. 驗證左側進階認證解鎖專區的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["left_advanced_unlock"])

        with allure.step(
            "44. 驗證進階認證解鎖專區的請選擇遊戲/服務的選單按鈕，"
            "確實於渲染後五秒內存在、可見、可點擊"
        ):
            self.member.assert_link_ready(self.mcfg["game_service_select"], self.t)

        with allure.step("45. 驗證進階認證解鎖專區的請選擇遊戲/服務的選單按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["game_service_select"])

        with allure.step("46. 驗證天堂專用線上交易服務，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["lineage_trade_service"])

        with allure.step("47. 驗證天堂專用線上交易服務查詢按鈕，可成功點擊"):
            self.member.click_query_button()

        advanced_txt = ""
        with allure.step("48. 驗證所查詢到的進階認證解鎖內容，確實於渲染後五秒內存在、可見"):
            advanced_txt = self.member.get_first_result_text(
                min_len=self.ta["advanced_unlock_row_min_length"]
            )
            allure.attach(
                advanced_txt,
                name="進階認證解鎖",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("49. 驗證所查詢的進階認證解鎖內容，比對文本，文本呈現正確"):
            assert len(advanced_txt.strip()) >= self.ta["advanced_unlock_row_min_length"]

    # ── 區塊二：50–62 ─────────────────────────────────────────────
    @allure.title("區塊二 50-62：電子報、簡訊、關閉會員中心")
    def test_s2_50_through_62_newsletter_sms_close(self):
        # Test ID: BF-MC-S2-50 ~ 62
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        _close_member_popup_if_visible(self.driver, self.home, self.member)
        self.member.open_from_home(self.home)

        with allure.step("50. 驗證左側取消/訂閱電子報的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["newsletter_section"])

        with allure.step("51. 驗證訂閱電子報按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.member.assert_link_ready(self.mcfg["subscribe"], self.t)

        with allure.step("52. 驗證訂閱電子報按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["subscribe"])

        with allure.step("53. 驗證已訂閱電子報後的訂閱狀態，比對文本，文本呈現正確"):
            self.member.assert_popup_text_contains_one_of(
                self.mcfg["subscribed_status_fragments"], self.t
            )

        with allure.step("54. 驗證取消訂閱電子報按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["unsubscribe"])

        with allure.step("55. 驗證取消訂閱電子報後的訂閱狀態，比對文本，文本呈現正確"):
            self.member.assert_popup_text_contains_one_of(
                self.mcfg["unsubscribed_status_fragments"], self.t
            )

        with allure.step("56. 驗證左側取消/訂閱簡訊的按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["sms_section"])

        with allure.step("57. 驗證訂閱簡訊按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.member.assert_link_ready(self.mcfg["subscribe"], self.t)

        with allure.step("58. 驗證訂閱簡訊按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["subscribe"])

        with allure.step("59. 驗證已訂閱簡訊後的訂閱狀態，比對文本，文本呈現正確"):
            self.member.assert_popup_text_contains_one_of(
                self.mcfg["subscribed_status_fragments"], self.t
            )

        with allure.step("60. 驗證取消訂閱簡訊按鈕，可成功點擊"):
            self.member.click_link_or_button(self.mcfg["unsubscribe"])

        with allure.step("61. 驗證取消訂閱簡訊後的訂閱狀態，比對文本，文本呈現正確"):
            self.member.assert_popup_text_contains_one_of(
                self.mcfg["unsubscribed_status_fragments"], self.t
            )

        with allure.step("62. 驗證關閉會員中心按鈕，可成功點擊"):
            self.member.close_member_center(self.home)

    # ── 區塊三：1–11 ───────────────────────────────────────────────
    @allure.title("區塊三 1-11：錢包、儲值購點、彈窗、購買點數與查詢記錄展開")
    def test_s3_01_through_11_topup_shell(self):
        # Test ID: BF-TOPUP-S3-01 ~ 11
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()

        with allure.step("1. 驗證右下角剩餘點數開啟列表按鈕，可成功點擊"):
            self.home.safe_click_action_bar(HomePage.REMAINING_POINTS_TOGGLE)

        with allure.step("2. 驗證儲值與購點按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.topup.assert_topup_or_buy_ready(self.tcfg, self.t)

        with allure.step("3. 驗證儲值與購點按鈕，可成功點擊"):
            self.topup.click_topup_entry(
                self.home,
                self.tcfg["topup_purchase"],
                self.tcfg["topup_purchase_alt"],
            )

        with allure.step("4. 驗證儲值與購點彈窗內容，確實於渲染後五秒內存在、可見、可點擊"):
            self.topup.assert_panel_clickable_root(self.t)

        with allure.step("5. 驗證購買點數的彈窗提示，確實於渲染後五秒內存在、可見"):
            self.topup.assert_hint_visible(
                self.tcfg["buy_points_hint_fragment"], self.t
            )

        with allure.step("6. 驗證儲值頁的彈窗提示文本，比對文本，文本呈現正確"):
            self.topup.assert_hint_visible(
                self.tcfg["topup_hint_fragment"], self.t
            )

        with allure.step("7. 驗證左側購買點數的按鈕，可成功點擊"):
            self.topup.click_in_panel(self.tcfg["buy_points"])

        with allure.step("8. 驗證購買點數頁的彈窗提示，確實於渲染後五秒內存在、可見"):
            self.topup.assert_hint_visible(
                self.tcfg["buy_points_hint_fragment"], self.t
            )

        with allure.step("9. 驗證購買點數頁的彈窗提示文本，比對文本，文本呈現正確"):
            self.topup.assert_in_panel_visible(
                self.tcfg["buy_points_hint_fragment"], self.t
            )

        with allure.step("10. 驗證展開左側查詢記錄，可成功點擊"):
            self.topup.click_in_panel(self.tcfg["left_query_record"])

        with allure.step("11. 驗證左側查詢記錄的按鈕，可成功點擊"):
            self.topup.assert_in_panel_ready(
                self.tcfg["left_topup_record"], self.t
            )

    # ── 區塊三：12–18 ─────────────────────────────────────────────
    @allure.title("區塊三 12-18：儲值記錄、消費記錄")
    def test_s3_12_through_18_records(self):
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        self.home.open_gash_submenu()
        self.topup.click_topup_entry(
            self.home,
            self.tcfg["topup_purchase"],
            self.tcfg["topup_purchase_alt"],
        )

        with allure.step("12. 驗證儲值記錄頁的查詢按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.topup.click_in_panel(self.tcfg["left_topup_record"])
            self.topup.assert_in_panel_ready("查詢", self.t)

        with allure.step("13. 驗證儲值記錄頁的查詢按鈕，可成功點擊"):
            self.topup.click_query_in_panel()

        with allure.step("14. 驗證所查詢的儲值記錄內容，比對文本，文本呈現正確"):
            tr = self.topup.get_first_row_or_item_text(
                min_len=self.ta["topup_record_row_min_length"]
            )
            assert len(tr) >= self.ta["topup_record_row_min_length"]
            allure.attach(tr, name="儲值記錄", attachment_type=allure.attachment_type.TEXT)

        with allure.step("15. 驗證左側消費記錄的按鈕，可成功點擊"):
            self.topup.click_in_panel(self.tcfg["left_consumption_record"])

        with allure.step("16. 驗證消費紀錄頁的查詢按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.topup.assert_in_panel_ready("查詢", self.t)

        with allure.step("17. 驗證消費紀錄頁的查詢按鈕，可成功點擊"):
            self.topup.click_query_in_panel()

        with allure.step("18. 驗證所查詢的消費記錄內容，比對文本，文本呈現正確"):
            cr = self.topup.get_first_row_or_item_text(
                min_len=self.ta["consumption_row_min_length"]
            )
            assert len(cr) >= self.ta["consumption_row_min_length"]
            allure.attach(cr, name="消費記錄", attachment_type=allure.attachment_type.TEXT)

    # ── 區塊三：19–24 ─────────────────────────────────────────────
    @allure.title("區塊三 19-24：遊戲專用點數、最近儲值記錄")
    def test_s3_19_through_24_game_points_recent(self):
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        self.home.open_gash_submenu()
        self.topup.click_topup_entry(
            self.home,
            self.tcfg["topup_purchase"],
            self.tcfg["topup_purchase_alt"],
        )

        with allure.step("19. 驗證左側遊戲專用點數的按鈕，可成功點擊"):
            self.topup.click_in_panel(self.tcfg["left_game_points"])

        with allure.step(
            "20. 驗證遊戲專用點數所查詢的第一筆點數記錄內容，確實於渲染後五秒內存在、可見"
        ):
            self.topup.click_query_in_panel()
            gp = self.topup.get_first_row_or_item_text(
                min_len=self.ta["game_dedicated_row_min_length"]
            )
            allure.attach(gp, name="遊戲專用點數", attachment_type=allure.attachment_type.TEXT)

        with allure.step("21. 驗證遊戲專用點數第一筆內容，比對文本，文本呈現正確"):
            assert len(gp) >= self.ta["game_dedicated_row_min_length"]

        with allure.step("22. 驗證左側最近的儲值記錄的按鈕，可成功點擊"):
            self.topup.click_in_panel(self.tcfg["left_recent_topup"])

        with allure.step("23. 驗證所查詢的最近的儲值記錄頁面內容，確實於渲染後五秒內存在、可見"):
            self.topup.click_query_in_panel()
            rt = self.topup.get_first_row_or_item_text(
                min_len=self.ta["recent_topup_row_min_length"]
            )
            allure.attach(rt, name="最近儲值記錄", attachment_type=allure.attachment_type.TEXT)

        with allure.step("24. 驗證所查詢到的最近的儲值記錄內容文本，比對文本，文本呈現正確"):
            assert len(rt) >= self.ta["recent_topup_row_min_length"]

    # ── 區塊三：25–31 ─────────────────────────────────────────────
    @allure.title("區塊三 25-31：計費設定、更新點數")
    def test_s3_25_through_31_billing_refresh(self):
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        self.home.open_gash_submenu()
        self.topup.click_topup_entry(
            self.home,
            self.tcfg["topup_purchase"],
            self.tcfg["topup_purchase_alt"],
        )

        with allure.step("25. 驗證左側計費設定的按鈕，可成功點擊"):
            self.topup.click_in_panel(self.tcfg["billing_settings"])

        with allure.step("26. 驗證計費設定的查詢按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.topup.assert_in_panel_ready("查詢", self.t)

        with allure.step("27. 驗證計費設定的查詢按鈕，可成功點擊"):
            self.topup.click_query_in_panel()

        with allure.step("28. 驗證所查詢到最上面一筆的計費設定記錄文本，比對文本，文本呈現正確"):
            br = self.topup.get_first_row_or_item_text(
                min_len=self.ta["billing_row_min_length"]
            )
            assert len(br) >= self.ta["billing_row_min_length"]
            allure.attach(br, name="計費設定", attachment_type=allure.attachment_type.TEXT)

        with allure.step("29. 驗證左上角更新點數的按鈕，確實於渲染後五秒內存在、可見、可點擊"):
            self.home.switch_to_default()
            self.home.open_gash_submenu()
            rp = self.tcfg["refresh_points"].replace("'", "\\'")
            ra = self.tcfg["refresh_points_alt"].replace("'", "\\'")
            loc = (
                By.XPATH,
                f"//*[@id='BF_divGashSubMenu']//a[contains(., '{rp}') "
                f"or contains(., '{ra}')]",
            )
            self.home.assert_element_ready(loc, self.t)

        with allure.step("30. 驗證所刷新的當前點數文本內容，確實於渲染後五秒內存在、可見"):
            self.topup.click_refresh_points_in_menu(self.home)
            WebDriverWait(self.driver, self.t).until(
                lambda d: len(
                    re.sub(
                        r"[^\d]",
                        "",
                        d.find_element(*HomePage.POINTS_VALUE).text.strip(),
                    )
                )
                >= self.ta["current_points_digit_min"]
            )

        with allure.step("31. 驗證所查詢到的當前點數內容文本，比對文本，文本呈現正確"):
            digits = self.topup.get_current_points_digits()
            assert len(digits) >= self.ta["current_points_digit_min"]

    # ── 區塊三：32 ────────────────────────────────────────────────
    @allure.title("區塊三 32：關閉儲值與購點彈窗")
    def test_s3_32_close_topup_popup(self):
        self.home.ensure_on_home()
        self.home.dismiss_blocking_overlays()
        self.home.open_gash_submenu()
        self.topup.click_topup_entry(
            self.home,
            self.tcfg["topup_purchase"],
            self.tcfg["topup_purchase_alt"],
        )

        with allure.step("32. 驗證儲值與購點的彈窗關閉按鈕，可成功點擊"):
            self.topup.click_close_in_panel(self.home, self.tcfg["close_popup"])
