import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

class HomePage(BasePage):
    # ════════════════════════════════════════════════
    # 定位器 (Locators)
    # ════════════════════════════════════════════════
    LOGO = (By.CSS_SELECTOR, "a.logo.oneBrand.bilingual")
    LOGIN_BTN = (By.ID, "BF_anchorLoginBtn")
    
    # 中段分類頁籤 (改用更穩定的結構定位，避免純文字)
    # 假設 HTML 結構為 <li class="tab-item" data-type="hot">...</li>
    TABS = {
        "hot": (By.XPATH, "//div[contains(text(), '熱門線上遊戲')]"),
        "popular": (By.XPATH, "//div[contains(text(), '超人氣手機遊戲')]"),
        "direct": (By.XPATH, "//div[contains(text(), '原廠直營遊戲')]")
    }
    
    # 遊戲列表容器 (用於驗證切換是否成功)
    TAB_LIST_CONTAINERS = {
        "hot": (By.ID, "hot-online-list-id"),
        "popular": (By.ID, "popular-mobile-list-id"),
        "direct": (By.ID, "direct-operated-list-id")
    }

    # 廣告與影音
    YOUTUBE_IFRAME = (By.XPATH, "//iframe[contains(@src, 'youtube.com')]")
    # YouTube 原生播放按鈕通常在加載後才會出現在 Iframe 內
    YOUTUBE_PLAY_BTN = (By.CSS_SELECTOR, ".ytp-large-play-button")
    YOUTUBE_PLAYING_STATUS = (By.CSS_SELECTOR, ".playing-mode") # 示意：播放後的狀態

    # ════════════════════════════════════════════════
    # 頁面操作方法
    # ════════════════════════════════════════════════
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://tw.beanfun.com/"

    def go_to_home(self):
        """前往首頁並確保加載完成"""
        self.driver.get(self.url)
        self.assert_element_visible(self.LOGO, timeout=15)

    def switch_tab_and_verify(self, tab_key):
        """
        切換遊戲分類頁籤並驗證內容顯示
        :param tab_key: 'hot', 'popular', 或 'direct'
        """
        tab_locator = self.TABS.get(tab_key)
        list_locator = self.TAB_LIST_CONTAINERS.get(tab_key)
        
        # 點擊頁籤
        tab_element = self.assert_element_ready(tab_locator)
        tab_element.click()
        
        # 動態等待：列表必須變為可見，且確保它沒有被隱藏屬性遮蓋
        self.assert_element_visible(list_locator, timeout=5)
        return True

    def switch_to_youtube_and_play(self, timeout=15):
        """
        處理 Youtube iframe 切換與播放 (嚴格遵守原生點擊)
        """
        # 1. 確保 iframe 已加載並切換
        iframe = self.assert_element_visible(self.YOUTUBE_IFRAME, timeout)
        self.driver.switch_to.frame(iframe)
        
        try:
            # 2. 點擊播放 (標準 API)
            play_btn = self.assert_element_ready(self.YOUTUBE_PLAY_BTN, timeout)
            play_btn.click()
            
            # 3. 驗證播放中狀態 (避免點擊後其實沒在播)
            # 這裡使用 presence_of_element 檢查 YT 的播放器 class 是否改變
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-state-playing")),
                message="YouTube 影片點擊後未進入播放狀態"
            )
        finally:
            # 強制切回主文件，避免後續定位失效
            self.driver.switch_to.default_content()

    def click_and_capture_redirect(self, locator, name_prefix):
        """點擊元素、等待 URL 變化並截圖 (移除 sleep)"""
        current_url = self.driver.current_url
        element = self.assert_element_ready(locator)
        element.click()
        
        # 動態等待：直到 URL 發生變化
        WebDriverWait(self.driver, 10).until(
            lambda d: d.current_url != current_url,
            message=f"點擊 {name_prefix} 後 URL 超時未跳轉"
        )
        
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=f"{name_prefix}_redirect_screenshot",
            attachment_type=allure.attachment_type.PNG
        )

 
    def assert_element_ready(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator), f"元素 {locator} 不可點擊"
        )

    def assert_element_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator), f"元素 {locator} 不可見"
        )