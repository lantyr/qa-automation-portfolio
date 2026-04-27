from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    ElementClickInterceptedException, 
    StaleElementReferenceException
)

class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, self.timeout)

    # 1. 核心等待：元素顯示
    def wait_until_visible(self, locator):
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            raise AssertionError(f"FAIL: 元素 {locator} 在 {self.timeout} 秒內未能顯示")

    # 2. 核心等待：元素可點擊
    def wait_until_clickable(self, locator):
        try:
            return self.wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            raise AssertionError(f"FAIL: 元素 {locator} 在 {self.timeout} 秒內無法點擊")

    # 3. 狀態判斷：元素是否顯示 (安全捕捉，禁用裸 except)
    def is_element_displayed(self, locator, timeout=None):
        """
        判斷元素是否顯示。可傳入較短的 timeout 以避免不必要的長時間等待。
        例如檢查偶發彈窗時：is_element_displayed(loc, timeout=2)
        """
        wait_time = timeout if timeout is not None else self.timeout
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # 4. 安全點擊機制 (根除 Flaky Test)
    def click_element_safely(self, locator):
        """
        嚴格動態等待點擊：忽略畫面遮擋 (Intercepted) 與 DOM 刷新 (Stale)，
        直到成功點擊或超時。
        """
        # 使用專屬的 Wait 來忽略特定干擾因素
        safe_wait = WebDriverWait(
            self.driver, 
            self.timeout, 
            poll_frequency=0.5, 
            ignored_exceptions=[
                ElementClickInterceptedException, 
                StaleElementReferenceException    
            ]
        )
        
        def _click_condition(driver):
            element = EC.element_to_be_clickable(locator)(driver)
            if element:
                element.click()
                return True
            return False

        try:
            safe_wait.until(_click_condition)
        except TimeoutException:
            raise AssertionError(f"FAIL: 元素 {locator} 無法點擊，可能一直被遮擋或動畫未結束")

    # ════════════════════════════════════════════════
    # 補充：為支援 HomePage 與其他頁面補齊的安全封裝方法
    # ════════════════════════════════════════════════

    # 5. 安全獲取文字
    def get_text(self, locator):
        """等待元素顯示後獲取其文本，自動去除前後空白，並防禦 DOM 刷新"""
        element = self.wait_until_visible(locator)
        try:
            return element.text.strip()
        except StaleElementReferenceException:
            # 若發生 Stale，重新抓取一次確保穩定
            element = self.wait_until_visible(locator)
            return element.text.strip()

    # 6. 安全獲取屬性值
    def get_attribute(self, locator, attribute):
        """等待元素存在後獲取指定屬性值"""
        try:
            # 屬性獲取通常只需要存在於 DOM 中即可 (presence)，不需要顯示 (visibility)
            element = self.wait.until(EC.presence_of_element_located(locator))
            return element.get_attribute(attribute)
        except TimeoutException:
            raise AssertionError(f"FAIL: 元素 {locator} 在 {self.timeout} 秒內未出現在 DOM 中，無法獲取屬性 {attribute}")
        except StaleElementReferenceException:
            element = self.wait.until(EC.presence_of_element_located(locator))
            return element.get_attribute(attribute)

    # 7. 安全獲取多個元素 (列表)
    def find_elements(self, locator):
        """
        等待至少一個符合條件的元素出現在 DOM 中，並回傳列表。
        若超時未找到，則回傳空列表 (符合 Selenium 原生行為，且不讓測試崩潰)。
        """
        try:
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            return []

    def check_for_rate_limit(self):
        """偵測網站是否回傳 429 Too Many Requests。

        【為什麼加自動等待而非直接 skip】
        429 是 beanfun 的 IP 級別速率限制，冷卻時間約 15 分鐘。
        原本偵測到就 pytest.skip()，導致後續所有測試全部跳過，需要人工等待後手動重跑。
        改為自動等待 15 分鐘並重試一次，讓排程跑完整輪無需人工介入。

        【為什麼用 sleep 而非條件等待（Rule 5 例外說明）】
        CLAUDE.md Rule 5 禁止寫死等待，應改用元素可見/消失等 UI 條件。
        但 IP 解封時間是伺服器端行為，沒有任何 UI 狀態可供偵測，
        屬於 Rule 5 明確允許的例外情境（無可偵測條件）。
        此處 sleep(900) 是已知冷卻時間的最小有效值，非猜測性等待。
        """
        import time
        import pytest
        from selenium.common.exceptions import UnexpectedAlertPresentException

        try:
            title = self.driver.title or ''
            src = self.driver.page_source[:500] if self.driver.page_source else ''
        except UnexpectedAlertPresentException:
            try:
                self.driver.switch_to.alert.accept()
            except Exception:
                pass
            return

        if '429' not in title and 'Too Many Requests' not in src and '429' not in src:
            return

        # 429 偵測到：等待 15 分鐘後重試一次
        time.sleep(900)
        self.driver.refresh()

        try:
            title = self.driver.title or ''
            src = self.driver.page_source[:500] if self.driver.page_source else ''
        except UnexpectedAlertPresentException:
            try:
                self.driver.switch_to.alert.accept()
            except Exception:
                pass
            return

        if '429' in title or 'Too Many Requests' in src or '429' in src:
            pytest.skip('被鎖定：429 Too Many Requests - 等待 15 分鐘後仍無法繼續')
