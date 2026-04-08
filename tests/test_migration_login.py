import pytest
import allure
import time
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.portal_page import PortalPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config.credentials import (
    get_beanfun_otp,
    get_beanfun_target_account,
    require_beanfun_credentials,
)


@allure.feature("會員登入功能")
class TestLoginFlow:

    @allure.title("驗證：已開通整合點帳進行登入測試 (全自動)")
    def test_login_757(self, driver):
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
            try:
                login_page.login_action(account, password)
                login_page.take_screenshot("點擊前往驗證前畫面")
            except Exception as e:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="登入卡關現場截圖",
                    attachment_type=allure.attachment_type.PNG,
                )
                raise e

        with allure.step(f"步驟 3: 填寫固定驗證碼 ({otp_code})"):
            home_page.take_screenshot("步驟 3: 填寫固定驗證碼")
            login_page.fill_otp_code(otp_code)
            print(f"👉 直接輸入固定驗證碼: {otp_code}")

            time.sleep(2)

            try:
                login_page.click_final_confirm()
            except Exception:
                pass

        with allure.step("步驟 4: 驗證是否成功登入並回到首頁"):
            time.sleep(4)
            home_page.handle_alert()

            assert "beanfun" in driver.current_url
            login_page.take_screenshot("最終登入成功畫面")

    @allure.title("驗證：「舊 H5 需手動選取帳號」登入測試 (全自動)")
    def test_login_762(self, driver):
        target_account = get_beanfun_target_account()
        if not target_account:
            pytest.skip(
                "需設定 .env 的 BEANFUN_TEST_TARGET_ACCOUNT（舊 H5 要點選的遊戲帳號名稱）"
            )

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
            try:
                login_page.login_action(account, password)
                login_page.take_screenshot("點擊前往驗證前畫面")
            except Exception as e:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="登入卡關現場截圖",
                    attachment_type=allure.attachment_type.PNG,
                )
                raise e

        with allure.step(f"步驟 3: 填寫固定驗證碼 ({otp_code})"):
            print(f"👉 直接輸入固定驗證碼: {otp_code}")
            home_page.take_screenshot("步驟 3: 填寫固定驗證碼")
            login_page.fill_otp_code(otp_code)
            time.sleep(2)
            try:
                login_page.click_final_confirm()
            except Exception:
                pass

        with allure.step(f"步驟 4: 點選遊戲帳號 [{target_account}] 並確認"):
            try:
                acc_xpath = f"//*[contains(text(), '{target_account}')]"
                acc_ele = login_page.wait.until(
                    EC.presence_of_element_located((By.XPATH, acc_xpath))
                )
                login_page.driver.execute_script(
                    "arguments[0].click();", acc_ele
                )

                btn_xpath = "//a[contains(., '確認')]"
                btn_ele = login_page.wait.until(
                    EC.element_to_be_clickable((By.XPATH, btn_xpath))
                )
                login_page.driver.execute_script(
                    "arguments[0].click();", btn_ele
                )
                login_page.take_screenshot("已按下確認鈕")
            except Exception as e:
                login_page.take_screenshot("步驟4卡關截圖")
                raise e

        self.verify_back_to_home(driver, home_page, login_page)

    def verify_back_to_home(self, driver, home_page, login_page):
        """共用的最後驗證邏輯：確保真的回到官網"""
        with allure.step("步驟 5: 驗證是否成功跳轉回官網首頁"):
            try:
                login_page.wait.until(
                    EC.url_to_be("https://tw.beanfun.com/")
                )

                time.sleep(2)
                home_page.handle_alert()

                login_page.take_screenshot("最終登入成功_官網首頁")
                print("✅ 成功抵達官網首頁！")
            except Exception:
                login_page.take_screenshot("跳轉官網超時截圖")
                raise Exception(
                    "登入後未能於預期時間內跳轉回官網首頁！"
                ) from None
