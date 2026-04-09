from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
import time
import allure

class LoginPage(BasePage):
    # ---  定位器 ---
    OTP_INPUTS = (By.CSS_SELECTOR, ".input-block input")
    STEP1_ACCOUNT = (By.XPATH, "//input[@placeholder='請輸入帳號']")
    STEP1_BTN = (By.XPATH, "//*[contains(text(), '登入帳號')]")
    PHONE_INPUT = (By.XPATH, "//input[@type='text' and contains(@class, 'el-input__inner')]")
    NEXT_BTN = (By.XPATH, "//button[contains(., '下一步')]")
    PWD_INPUT = (By.XPATH, "//input[@type='password']")
    LOGIN_FINAL_BTN = (By.XPATH, "//button[contains(., '登入')]")
    GO_TO_VERIFY_BTN = (By.XPATH, "//button[contains(., '前往驗證')] | //span[contains(text(), '前往驗證')]/..")
    FINAL_CONFIRM_BTN = (By.XPATH, "//button[contains(., '確定')] | //span[contains(text(), '確定')]/..")
    
    # 驗證碼輸入框的定位器
    OTP_INPUTS = (By.XPATH, "//div[contains(@class, 'input-block')]//input")
    GP_MODAL_TITLE = (By.XPATH, "//*[contains(text(), '繼續以 Gama Pass 登入')]")
    GP_MODAL_GOTO_BTN = (By.XPATH, "//button[contains(., '前往登入')] | //a[contains(., '前往登入')]")
    
    # 密碼欄位 (用來驗證它有沒有出現)
    PWD_INPUT_AREA = (By.XPATH, "//input[@type='password']")

    # 純點帳同視窗流程
    PURE_PWD_INPUT = (By.XPATH, "//input[@placeholder='請輸入密碼']")
    CONTINUE_BTN   = (By.XPATH, "//a[contains(@class,'ui-btn')]//span[text()='繼續']/..")

    # 帳號選擇步驟（GP點帳登入後可能出現）
    ACCOUNT_RADIO_FIRST = (By.XPATH, "(//label[.//input[@type='radio' and @name='account']])[1]")
    CONFIRM_BTN         = (By.XPATH, "//a[contains(@class,'ui-btn')]//span[text()='確認']/..")
    #  異常測試定位器
   #  升級版異常測試定位器 (同時捕捉小紅字與置中彈窗)
    ERROR_MSG = (By.XPATH, "//div[contains(@class, 'el-message--error')] | //div[contains(@class, 'error-msg')] | //div[contains(@class, 'el-message-box__content')]")
    TIP_MSG = (By.XPATH, "//*[contains(text(), '請輸入') or contains(text(), '格式錯誤')]")

    # ---  頁面動作 ---
    #  新增 wait_for_verify 開關，預設為 True (正常流程)
    def login_action(self, phone, password, wait_for_verify=True):
        self.handle_announcement()
        
        print("[1/4] 正在填寫初始帳號並點擊登入...")
        old_handles = self.driver.window_handles
        account_el = self.wait_until_visible(self.STEP1_ACCOUNT)
        account_el.click()
        account_el.send_keys(phone)
        btn_element = self.wait_until_visible(self.STEP1_BTN)
        self.driver.execute_script("arguments[0].click();", btn_element)
        self.wait_and_switch_window(old_handles)
        self.wait_and_switch_window(old_handles)

        print(f"[2/4] 正在填寫帳號: {phone}")
        phone_el = self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))
        phone_el.click()
        phone_el.send_keys(Keys.CONTROL, 'a')
        phone_el.send_keys(phone)
        
        next_btn = self.wait.until(EC.element_to_be_clickable(self.NEXT_BTN))
        self.driver.execute_script("arguments[0].click();", next_btn)

        print(f" [3/4] 正在填寫密碼...")
        time.sleep(2)
        pwd_el = self.wait.until(EC.visibility_of_element_located(self.PWD_INPUT))
        pwd_el.send_keys(password)

        handles_before_login = self.driver.window_handles
        login_btn = self.wait_until_visible(self.LOGIN_FINAL_BTN)
        self.driver.execute_script("arguments[0].click();", login_btn)
        print(" 已按下登入...")

        #  如果是異常測試（密碼錯誤），到這裡就結束，不等待驗證彈窗！
        if not wait_for_verify:
            return

        self.wait_and_switch_window(handles_before_login)
        print(" 正在等待前往驗證出現...")
        try:
            verify_btn = self.wait.until(EC.visibility_of_element_located(self.GO_TO_VERIFY_BTN))
            self.driver.execute_script("arguments[0].click();", verify_btn)
            print(" 成功點擊前往驗證按鈕！")
        except Exception:
            print(" 直接定位失敗，嘗試掃描 Iframe...")
            if self.scan_iframes_and_click(self.GO_TO_VERIFY_BTN):
                print(" 在 Iframe 中成功點擊前往驗證")
            else:
                print(" 窮盡所有方法仍找不到前往驗證按鈕")
                allure.attach(self.driver.get_screenshot_as_png(), name="最後找不到按鈕的畫面", attachment_type=allure.attachment_type.PNG)
                raise Exception("無法定位前往驗證按鈕")

    def select_first_account_and_confirm(self, timeout: int = 15) -> None:
        """
        選取第一個遊戲帳號 radio button 並點擊確認。
        GP點帳（gamaplay830）輸入密碼後可能出現此帳號選擇頁。
        依序嘗試：所有已開視窗 × (主文件 + 所有 iframe)。
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC_inner

        all_handles = self.driver.window_handles
        for handle in reversed(all_handles):  # 從最新視窗往前找
            try:
                self.driver.switch_to.window(handle)
            except Exception:
                continue

            # 主文件
            self.driver.switch_to.default_content()
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC_inner.element_to_be_clickable(self.ACCOUNT_RADIO_FIRST)
                )
                self.click_element_safely(self.ACCOUNT_RADIO_FIRST)
                self.click_element_safely(self.CONFIRM_BTN)
                self.driver.switch_to.default_content()
                return
            except Exception:
                pass

            # 掃描 iframe
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for i in range(len(iframes)):
                try:
                    self.driver.switch_to.default_content()
                    self.driver.switch_to.frame(i)
                    WebDriverWait(self.driver, 3).until(
                        EC_inner.element_to_be_clickable(self.ACCOUNT_RADIO_FIRST)
                    )
                    self.click_element_safely(self.ACCOUNT_RADIO_FIRST)
                    self.click_element_safely(self.CONFIRM_BTN)
                    self.driver.switch_to.default_content()
                    return
                except Exception:
                    continue

        self.driver.switch_to.default_content()
        raise AssertionError("FAIL: 找不到帳號選擇 radio button（所有視窗與 iframe 均未找到）")

    def login_action_pure(self, account, password):
        """
        純點帳登入：密碼欄出現在帳號欄下方（同視窗，無 GamaPass 跳轉）
        流程：帳號  點登入帳號 密碼欄出現  密碼  點繼續
        """
        self.handle_announcement()
        account_el = self.wait_until_visible(self.STEP1_ACCOUNT)
        account_el.click()
        account_el.send_keys(account)
        btn_element = self.wait_until_visible(self.STEP1_BTN)
        self.driver.execute_script("arguments[0].click();", btn_element)
        pwd_el = self.wait_until_visible(self.PURE_PWD_INPUT)
        pwd_el.click()
        pwd_el.send_keys(password)
        self.click_element_safely(self.CONTINUE_BTN)

    def fill_otp_code(self, otp_code):
        print(f" 準備將驗證碼 {otp_code} 填入畫面...")
        try:
            inputs = self.wait.until(EC.presence_of_all_elements_located(self.OTP_INPUTS))
            if len(inputs) == 4:
                for i, digit in enumerate(otp_code):
                    inputs[i].send_keys(digit)
                    time.sleep(0.2) 
                print(" 4 位數驗證碼填寫完成！")
            else:
                print(f" 預期要有 4 個格子，但只找到 {len(inputs)} 個")
        except Exception as e:
            print(f" 填寫驗證碼失敗: {e}")
            raise e

    def click_final_confirm(self):
        try:
            print(" 嘗試點擊最終 [確定]...")
            final_btn = self.wait.until(EC.element_to_be_clickable(self.FINAL_CONFIRM_BTN))
            self.driver.execute_script("arguments[0].click();", final_btn)
            print(" 登入流程圓滿完成！")
        except:
            print(" 找不到最終確定按鈕，可能頁面已自動切換")

    def get_error_text(self):
        """地毯式搜索錯誤提示，同時支持密碼錯誤與忘記密碼"""
        print(" 開始掃描畫面上的錯誤訊息...")
        
        possible_locators = [
            # 1. 偵測 Element UI 的彈窗訊息內容
            (By.XPATH, "//div[contains(@class, 'el-message-box__message')]"),
            # 2. 偵測輸入框下方的小紅字
            (By.XPATH, "//div[contains(@class, 'el-message--error')]"),
            # 3.  終極捕捉：只要畫面出現這兩個關鍵字之一就抓下來
            (By.XPATH, "//*[contains(text(), '密碼錯誤') or contains(text(), '忘記密碼')]")
        ]

        # 稍微加長一點等待時間，確保彈窗完全跑出來
        end_time = time.time() + 5 
        while time.time() < end_time:
            for loc in possible_locators:
                try:
                    elements = self.driver.find_elements(*loc)
                    for el in elements:
                        if el.is_displayed() and len(el.text.strip()) > 0:
                            msg = el.text.strip()
                            print(f" 成功捕捉到錯誤內容: {msg}")
                            return msg
                except:
                    continue
            time.sleep(0.5)
            
        return ""

    def take_screenshot(self, name):
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )

    # ---  輔助方法 ---
    def wait_and_switch_window(self, old_handles):
        try:
            self.wait.until(lambda d: len(d.window_handles) > len(old_handles))
            new_handle = self.driver.window_handles[-1]
            self.driver.switch_to.window(new_handle)
            self.driver.maximize_window()
            print(f" 成功切換視窗: {self.driver.title}")
        except:
            pass

    def scan_iframes_and_click(self, locator):
        self.driver.switch_to.default_content()
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        for i, frame in enumerate(iframes):
            try:
                self.driver.switch_to.frame(i)
                targets = self.driver.find_elements(*locator)
                if len(targets) > 0:
                    self.driver.execute_script("arguments[0].click();", targets[0])
                    return True
                self.driver.switch_to.default_content()
            except:
                self.driver.switch_to.default_content()
        return False

    def handle_announcement(self):
        try:
            close_btn = (By.XPATH, "//button//span[contains(text(), '確定')]")
            if len(self.driver.find_elements(*close_btn)) > 0:
                self.driver.execute_script("arguments[0].click();", self.driver.find_element(*close_btn))
        except:
            pass
class TestData:
    # 這裡存放所有登入情境的資料
    MIGRATION_ACCOUNTS = [
        {
            "id": "757",
            "desc": "已整合點帳 (直通官網)",
            "user": "gamaplay757@gamapass.com",
            "pwd": "Qq1234567",
            "otp": "9999",
            "target": None  # None 代表不需要選帳號步驟
        },
        {
            "id": "762",
            "desc": "舊H5點帳 (需選帳號)",
            "user": "gamaplay762@gamapass.com",
            "pwd": "Qq1234567",
            "otp": "9999",
            "target": "lilia25081808" # 預期要點選的帳號名字
        }
    ]