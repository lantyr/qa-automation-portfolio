import allure
import time
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.portal_page import PortalPage

from config.credentials import get_beanfun_otp, require_beanfun_credentials


@allure.feature("會員登入功能")
class TestLoginFlow:

    @allure.title("驗證：EMAIL登入純點帳進行登入測試 (全自動)")
    def test_invalid_login(self, driver):
        home_page = HomePage(driver)
        portal_page = PortalPage(driver)
        login_page = LoginPage(driver)

        account, password = require_beanfun_credentials()
        otp_code = get_beanfun_otp()

        with allure.step("步驟 1: 前往首頁並點擊登入"):
            home_page.go_to_home()
            home_page.click_login_btn()
            home_page.take_screenshot("點擊首頁登入按鈕後")

        with allure.step(f"步驟 2: 執行帳密登入 ({account})"):
            login_page.take_screenshot(f"步驟 2: 執行帳密登入 ({account})")
            login_page.login_action(account, password)

        with allure.step(f"步驟 3: 填寫固定萬用驗證碼 ({otp_code})"):
            login_page.fill_otp_code(otp_code)
            login_page.click_final_confirm()

        with allure.step("步驟 4: 驗證最終登入結果"):
            time.sleep(5)
            home_page.handle_alert()
            allure.attach(
                driver.get_screenshot_as_png(),
                name="最終畫面",
                attachment_type=allure.attachment_type.PNG,
            )
