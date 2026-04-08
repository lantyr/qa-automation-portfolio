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
    def is_element_displayed(self, locator):
        try:
            self.wait_until_visible(locator)
            return True
        except AssertionError:
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