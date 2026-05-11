from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from .base_page import BasePage
import pytest
import random
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
    FINAL_CONFIRM_BTN = (By.XPATH,
        "//button[contains(., '確定')] | //span[contains(text(), '確定')]/.. | //a[contains(@class,'ui-btn')]//span[text()='繼續']/..")
    
    # 驗證碼輸入框的定位器（支援 input-block 格式 及 簡訊OTP單格 maxlength=1 格式）
    OTP_INPUTS = (By.XPATH,
        "//div[contains(@class, 'input-block')]//input | //input[@maxlength='1']")
    GP_MODAL_TITLE = (By.XPATH, "//*[contains(text(), '繼續以 Gama Pass 登入')]")
    GP_MODAL_GOTO_BTN = (By.XPATH, "//button[contains(., '前往登入')] | //a[contains(., '前往登入')]")
    
    # 密碼欄位 (用來驗證它有沒有出現)
    PWD_INPUT_AREA = (By.XPATH, "//input[@type='password']")

    # 純點帳同視窗流程
    PURE_PWD_INPUT = (By.XPATH, "//input[@placeholder='請輸入密碼']")
    CONTINUE_BTN   = (By.XPATH, "//a[contains(@class,'ui-btn')]//span[text()='繼續']/..")

    # 帳號選擇步驟（GP點帳登入後可能出現）
    ACCOUNT_RADIO_FIRST = (By.XPATH, "(//label[.//input[@type='radio']])[1]")
    CONFIRM_BTN         = (By.XPATH, "//a[contains(@class,'ui-btn')]//span[text()='確認']/.. | //a[contains(@class,'ui-btn')]//span[text()='繼續']/..")

    # 「您的帳號尚未完成開通」彈窗確認按鈕
    NOT_ACTIVATED_BTN = (By.XPATH,
        "//button[contains(., '我知道了')] | //a[contains(., '我知道了')] | //span[text()='我知道了']/..")

    # beanfun 登入頁「使用 Gama Pass」入口按鈕
    USE_GAMAPASS_BTN = (By.CSS_SELECTOR, "a.use-gama-pass")

    # OTP 送出 + gbox 彈窗確認（beanfun 簡訊OTP流程）
    OTP_SUBMIT_BTN = (By.CSS_SELECTOR, "a.btn.btn-send-otp")
    GBOX_CONFIRM_BTN = (By.CSS_SELECTOR, ".gbox-action a.gbox-btn")

    # 資料驗證-手機(6碼) 頁面指示文字
    PHONE_VERIFY_HINT = (By.XPATH,
        "//*[contains(text(), '資料驗證') or contains(text(), '手機') and contains(text(), '碼')]")
    #  異常測試定位器
   #  升級版異常測試定位器 (同時捕捉小紅字與置中彈窗)
    ERROR_MSG = (By.XPATH, "//div[contains(@class, 'el-message--error')] | //div[contains(@class, 'error-msg')] | //div[contains(@class, 'el-message-box__content')]")
    TIP_MSG = (By.XPATH, "//*[contains(text(), '請輸入') or contains(text(), '格式錯誤')]")

    # ---  頁面動作 ---
    #  新增 wait_for_verify 開關，預設為 True (正常流程)
    def _handle_captcha_alert(self):
        """偵測並接受 CAPTCHA 驗證對話框，出現時自動 SKIP 測試。"""
        try:
            alert = self.driver.switch_to.alert
            text = alert.text or ''
            alert.accept()
            if '機器人' in text or 'CAPTCHA' in text.upper():
                pytest.skip(f"CAPTCHA 出現（{text}），網站偵測到自動化瀏覽器，請稍後重試")
        except Exception:
            pass

    def login_action(self, phone, password, wait_for_verify=True):
        self.handle_announcement()
        self._handle_captcha_alert()
        
        print("[1/4] 正在填寫初始帳號並點擊登入...")
        old_handles = self.driver.window_handles
        try:
            account_el = self.wait_until_visible(self.STEP1_ACCOUNT)
        except UnexpectedAlertPresentException:
            self._handle_captcha_alert()
        account_el.click()
        self._human_type(account_el, phone)
        btn_element = self.wait_until_visible(self.STEP1_BTN)
        self.driver.execute_script("arguments[0].click();", btn_element)
        self.wait_and_switch_window(old_handles)
        self.wait_and_switch_window(old_handles)

        print(f"[2/4] 正在填寫帳號: {phone}")
        try:
            phone_el = self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))
        except UnexpectedAlertPresentException:
            self._handle_captcha_alert()
            phone_el = self.wait.until(EC.visibility_of_element_located(self.PHONE_INPUT))
        phone_el.click()
        phone_el.send_keys(Keys.CONTROL + 'a')
        self._human_type(phone_el, phone)

        next_btn = self.wait.until(EC.element_to_be_clickable(self.NEXT_BTN))
        self.driver.execute_script("arguments[0].click();", next_btn)

        print(f" [3/4] 正在填寫密碼...")
        pwd_el = self.wait.until(EC.visibility_of_element_located(self.PWD_INPUT))
        pwd_el.click()
        self._human_type(pwd_el, password)

        handles_before_login = self.driver.window_handles
        login_btn = self.wait_until_visible(self.LOGIN_FINAL_BTN)
        self.driver.execute_script("arguments[0].click();", login_btn)
        print(" 已按下登入...")

        #  如果是異常測試（密碼錯誤），到這裡就結束，不等待驗證彈窗！
        if not wait_for_verify:
            return

        print(" 正在等待前往驗證出現...")
        # 先在目前視窗找（GamaPass message-box 彈窗形式）；找不到才切換新視窗
        from selenium.webdriver.support.ui import WebDriverWait as _WDW
        try:
            verify_btn = _WDW(self.driver, 15, poll_frequency=0.5).until(
                EC.visibility_of_element_located(self.GO_TO_VERIFY_BTN)
            )
            self.driver.execute_script("arguments[0].click();", verify_btn)
            print(" 成功點擊前往驗證按鈕！")
        except Exception:
            self.wait_and_switch_window(handles_before_login)
            try:
                verify_btn = self.wait.until(EC.visibility_of_element_located(self.GO_TO_VERIFY_BTN))
                self.driver.execute_script("arguments[0].click();", verify_btn)
                print(" 在新視窗中成功點擊前往驗證按鈕！")
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
            _RADIO_SPAN = (By.XPATH, "(//label[.//input[@type='radio']]//span)[1]")
            self.driver.switch_to.default_content()
            try:
                radio_span = WebDriverWait(self.driver, timeout).until(
                    EC_inner.element_to_be_clickable(_RADIO_SPAN)
                )
                radio_span.click()
                confirm = WebDriverWait(self.driver, 5).until(
                    EC_inner.element_to_be_clickable(self.CONFIRM_BTN)
                )
                confirm.click()
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
                    radio_span = WebDriverWait(self.driver, 3).until(
                        EC_inner.element_to_be_clickable(_RADIO_SPAN)
                    )
                    radio_span.click()
                    confirm = WebDriverWait(self.driver, 5).until(
                        EC_inner.element_to_be_clickable(self.CONFIRM_BTN)
                    )
                    confirm.click()
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
            if len(inputs) in (4, 6):
                for i, digit in enumerate(otp_code[:len(inputs)]):
                    inputs[i].send_keys(digit)
                    time.sleep(0.2)
                print(f" {len(inputs)} 位數驗證碼填寫完成！")
            else:
                print(f" 預期 4 或 6 個輸入格，但找到 {len(inputs)} 個")
        except Exception as e:
            print(f" 填寫驗證碼失敗: {e}")
            raise e

    def dismiss_not_activated_dialog(self, timeout: int = 10):
        """點擊「您的帳號尚未完成開通」彈窗中的[我知道了]按鈕。"""
        from selenium.webdriver.support.ui import WebDriverWait as _WDW
        try:
            btn = _WDW(self.driver, timeout).until(
                EC.element_to_be_clickable(self.NOT_ACTIVATED_BTN)
            )
            self.driver.execute_script("arguments[0].click();", btn)
            print(" 已點擊「我知道了」")
        except Exception as e:
            print(f" 未出現「尚未開通」彈窗或無法點擊: {e}")
            raise e

    def assert_phone_verification_page(self, timeout: int = 15):
        """確認已進入資料驗證-手機(6碼) 頁面（等待「簡訊OTP驗證」標題出現）。"""
        from selenium.webdriver.support.ui import WebDriverWait as _WDW
        SMS_OTP_TITLE = (By.XPATH,
            "//*[contains(text(), '簡訊OTP') or contains(text(), 'OTP驗證碼') or contains(text(), 'OTP驗證')]")
        _WDW(self.driver, timeout).until(
            EC.visibility_of_element_located(SMS_OTP_TITLE)
        )
        print(" 已進入簡訊OTP驗證頁面")

    def submit_otp_and_confirm(self, timeout: int = 15):
        """OTP 填完後：點「確認」送出 → 等 gbox 彈窗 → 點彈窗「確認」。"""
        from selenium.webdriver.support.ui import WebDriverWait as _WDW
        _WDW(self.driver, timeout).until(
            EC.element_to_be_clickable(self.OTP_SUBMIT_BTN)
        ).click()
        print(" 已點擊 OTP 確認送出")
        # headless 模式下 gbox 彈窗可能延遲，加長等待並用 JS 點擊確保觸發
        btn = _WDW(self.driver, timeout).until(
            EC.element_to_be_clickable(self.GBOX_CONFIRM_BTN)
        )
        self.driver.execute_script("arguments[0].click();", btn)
        print(" 已點擊 gbox 彈窗確認")

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

    def switch_to_new_window(self, old_handles, timeout=15):
        """等待新視窗出現並切換過去。比 wait_and_switch_window 更嚴格：失敗時拋出例外。"""
        from selenium.webdriver.support.ui import WebDriverWait as _WDW
        _WDW(self.driver, timeout).until(
            lambda d: len(d.window_handles) > len(old_handles)
        )
        new_handle = [h for h in self.driver.window_handles if h not in old_handles][0]
        self.driver.switch_to.window(new_handle)
        self.driver.maximize_window()

    def _human_type(self, element, text: str) -> None:
        """逐字輸入並附加隨機延遲以模擬人類打字，防止 GamaPass 機器人偵測機制觸發。"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.08, 0.25))

    def login_on_gamapass_window(self, phone, password):
        """
        在 GamaPass 視窗中完成帳密登入（不含 OTP / 前往驗證）。
        前提：driver 已切換至 GamaPass 視窗。
        """
        phone_el = self.wait_until_visible(self.PHONE_INPUT)
        phone_el.click()
        phone_el.send_keys(Keys.CONTROL, 'a')
        self._human_type(phone_el, phone)

        self.click_element_safely(self.NEXT_BTN)

        pwd_el = self.wait_until_visible(self.PWD_INPUT)
        self._human_type(pwd_el, password)

        self.click_element_safely(self.LOGIN_FINAL_BTN)