import pytest
import allure
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.portal_page import PortalPage

@allure.feature("PC版官網登入頁")
class TestNegativeLogin:

    @allure.title("驗證網站標題與初始狀態")
    def test_initial_state(self, driver):
        home_page = HomePage(driver)
        with allure.step("1. 開啟官網網址"):
            home_page.go_to_home()
            home_page.take_screenshot("首頁開啟成功") # 📸 動作截圖
            
        with allure.step("2. 驗證網站標題是否為：遊戲橘子"):
            assert "遊戲橘子" in driver.title
            home_page.take_screenshot("標題驗證畫面") # 📸 動作截圖
            
        with allure.step("3. 驗證成功引導至預期網址"):
            assert "tw.beanfun.com" in driver.current_url
            home_page.take_screenshot("網址確認畫面") # 📸 動作截圖

    @allure.title("驗證登入流程異常處理：密碼錯誤/鎖定")
    def test_wrong_password(self, driver):
        login_page = LoginPage(driver)
        self.common_setup(driver)
        
        with allure.step("1. 驗證於登入頁輸入正確帳號但錯誤密碼"):
            login_page.login_action("0983481944", "WrongPassword123", wait_for_verify=False)
            login_page.take_screenshot("按下登入鈕後之畫面") # 📸 動作截圖
            
        with allure.step("2. 驗證錯誤提示彈窗 (密碼錯誤/忘記密碼)"):
            time.sleep(3)
            error = login_page.get_error_text()
            login_page.take_screenshot("偵測到錯誤訊息") # 📸 動作截圖
            assert len(error) > 0

    @allure.title("驗證欄位空值檢核")
    def test_empty_values(self, driver):
        login_page = LoginPage(driver)
        self.common_setup(driver)
        with allure.step("1. 驗證什麼都不填直接點擊登入之行為"):
            btn = login_page.wait.until(EC.presence_of_element_located(login_page.STEP1_BTN))
            login_page.driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
            login_page.take_screenshot("空值警告畫面") # 📸 動作截圖

    @allure.title("驗證格式錯誤檢核")
    def test_invalid_format(self, driver):
        login_page = LoginPage(driver)
        self.common_setup(driver)
        with allure.step("1. 驗證輸入少一碼的手機號碼並點擊登入"):
            login_page.wait_until_visible(login_page.STEP1_ACCOUNT).send_keys("098348194")
            login_page.take_screenshot("帳號少一碼輸入狀態") # 📸 動作截圖
            btn = login_page.wait.until(EC.presence_of_element_located(login_page.STEP1_BTN))
            login_page.driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
            login_page.take_screenshot("格式錯誤提示畫面") # 📸 動作截圖

    def common_setup(self, driver):
        home_page = HomePage(driver)
        portal_page = PortalPage(driver)
        home_page.go_to_home()
        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert.accept() 
        except:
            pass 
        home_page.click_login_btn()
        time.sleep(2)
        portal_page.click_gama_portal()