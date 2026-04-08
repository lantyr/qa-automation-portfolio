from selenium.webdriver.common.by import By
from pages.base_page import BasePage
import os

class HomePage(BasePage):
    # ════════════════════════════════════════════════
    # 定位器 (Locators) - 確保命名與呼叫一致
    # ════════════════════════════════════════════════
    LOGO = (By.CSS_SELECTOR, "a.logo.oneBrand.bilingual")
    
    # --- Banner 區塊 ---
    BANNER_IFRAME = ('id', 'actual_iframe_id_here') # ⚠️ 原腳本缺失
    BANNER_CONTAINER = (By.CSS_SELECTOR, "ul.bxslider")
    ACTIVE_BANNER_LINK = (By.CSS_SELECTOR, "ul.bxslider li.pic:not([style*='display: none']) a.pic")
    BANNER_NEXT_BTN = (By.CSS_SELECTOR, "a.slider-r-btn")
    
    # --- 最新消息區塊 ---
    NEWS_CONTAINER = (By.CSS_SELECTOR, "div.newsitem")
    NEWS_LIST_ITEMS = (By.CSS_SELECTOR, "div.newsitem ul li") # ⚠️ 原腳本缺失
    NEWS_FIRST_ITEM_LINK = (By.CSS_SELECTOR, "div.newsitem ul li:nth-child(1) a")
    NEWS_FIRST_ITEM_TXT = (By.CSS_SELECTOR, "div.newsitem ul li:nth-child(1) a span.title") # ⚠️ 原腳本缺失
    
    # --- Chatbot 區塊 ---
    CHATBOT_BTN = (By.ID, "gim-bot-tool-button")
    CHATBOT_WINDOW_TITLE = (By.XPATH, "//h3[contains(text(), '遊戲橘子客服小幫手')]")

    # --- 登入 / 登出 ---
    # ⚠️ 需依實際 DOM 調整
    LOGIN_BTN = (By.XPATH,
        "//*[@id='BF_btnCoLogin'] | //a[contains(@class,'co-login')] | "
        "//a[normalize-space()='登入' and not(ancestor::footer)]"
    )
    LOGOUT_BTN = (By.XPATH,
        "//*[@id='BF_btnLogout'] | //a[contains(@class,'logout') or normalize-space()='登出']"
    )

    # --- GASH 點數子選單 ---
    # ⚠️ 需依實際 DOM 調整 - 右下角「點數」展開按鈕與子選單
    REMAINING_POINTS_TOGGLE = (By.XPATH,
        "//*[contains(@id,'GashSubMenuLink') or contains(@id,'GashToggle')] | "
        "//*[@id='BF_divGashSubMenu']/preceding-sibling::a[1]"
    )
    GASH_SUBMENU = (By.ID, "BF_divGashSubMenu")
    TOPUP_PURCHASE_LINK = (By.XPATH,
        "//*[@id='BF_divGashSubMenu']//a[contains(.,'儲值與購點') or contains(.,'購點')]"
    )

    # --- 頁尾連結 ---
    # ⚠️ 需依實際 DOM 調整
    FOOTER_CS_LINK = (By.XPATH,
        "//footer//a[contains(.,'客服中心')] | "
        "//div[contains(@class,'footer') or contains(@id,'footer')]//a[contains(.,'客服中心')]"
    )

    def __init__(self, driver):
        super().__init__(driver)
        # 從環境變數讀取，若無則給予預設值 (遵守 Rule 8)
        self.url = os.getenv("BASE_URL", "https://tw.beanfun.com/")

    # ════════════════════════════════════════════════
    # 頁面行為 (Page Actions) - 統一依賴 BasePage 的封裝
    # ════════════════════════════════════════════════
    def go_to_home(self):
        """導航至首頁並等待 LOGO 出現。"""
        self.driver.get(self.url)
        self.wait_until_visible(self.LOGO)

    def open_homepage(self):
        self.driver.get(self.url)
        self.wait_until_visible(self.LOGO)

    def _switch_to_banner_iframe(self):
        self.driver.switch_to.default_content() 
        iframe_element = self.wait_until_visible(self.BANNER_IFRAME)
        self.driver.switch_to.frame(iframe_element)

    def is_hero_banner_visible(self):
        self._switch_to_banner_iframe()
        # 統一使用 BasePage 封裝的布林判斷方法
        is_visible = self.is_displayed(self.BANNER_CONTAINER)
        self.driver.switch_to.default_content()
        return is_visible

    def switch_hero_banner_next(self):
        self._switch_to_banner_iframe()
        self.click_element(self.BANNER_NEXT_BTN)
        self.driver.switch_to.default_content()

    def click_hero_banner(self):
        self._switch_to_banner_iframe()
        self.click_element(self.ACTIVE_BANNER_LINK)
        self.driver.switch_to.default_content()

    def get_current_banner_href(self):
        self._switch_to_banner_iframe()
        href = self.get_attribute(self.ACTIVE_BANNER_LINK, "href")
        self.driver.switch_to.default_content()
        return href

    # --- News Actions ---
    def verify_news_ready(self):
        return self.is_displayed(self.NEWS_CONTAINER)

    def get_first_news_title(self):
        return self.get_text(self.NEWS_FIRST_ITEM_TXT)

    def is_news_list_populated(self):
        # 避免直接用 driver.find_elements，交給 BasePage 處理
        elements = self.find_elements(self.NEWS_LIST_ITEMS)
        return len(elements) > 0

    def click_first_news(self):
        self.click_element(self.NEWS_FIRST_ITEM_LINK)

    # --- Chatbot Actions ---
    def verify_chatbot_ready(self):
        return self.is_displayed(self.CHATBOT_BTN)

    def click_chatbot(self):
        self.click_element(self.CHATBOT_BTN)

    def verify_chatbot_opened(self):
        return self.is_displayed(self.CHATBOT_WINDOW_TITLE)

    # --- 登入 / 彈窗處理 Actions ---
    def click_login_btn(self):
        """點擊首頁共用登入按鈕。"""
        self.click_element_safely(self.LOGIN_BTN)

    def handle_alert(self):
        """如有瀏覽器 alert 則接受，否則忽略。"""
        from selenium.common.exceptions import NoAlertPresentException
        try:
            self.driver.switch_to.alert.accept()
        except NoAlertPresentException:
            pass

    def dismiss_blocking_overlays(self):
        """嘗試關閉首頁可能出現的遮蔽層（廣告、公告彈窗等）。"""
        close_patterns = [
            (By.XPATH, "//div[contains(@class,'overlay') or contains(@class,'modal')]"
                       "//a[contains(@class,'close') or contains(@class,'btn_close')]"),
            (By.CSS_SELECTOR, ".modal .close, .popup .close, [id*='Close'][class*='btn']"),
        ]
        for locator in close_patterns:
            try:
                for el in self.driver.find_elements(*locator):
                    if el.is_displayed():
                        el.click()
            except Exception:
                pass

    # --- 儲值與購點 Actions ---
    def open_topup_popup(self):
        """
        展開 GASH 點數子選單，再點擊「儲值與購點」進入彈窗。
        ⚠️ REMAINING_POINTS_TOGGLE / TOPUP_PURCHASE_LINK 需依實際 DOM 調整。
        """
        self.click_element_safely(self.REMAINING_POINTS_TOGGLE)
        self.wait_until_visible(self.GASH_SUBMENU)
        self.click_element_safely(self.TOPUP_PURCHASE_LINK)

    # --- 頁尾 Actions ---
    def scroll_to_footer(self):
        """捲動至頁面底部使頁尾連結可見。"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.wait_until_visible(self.FOOTER_CS_LINK)

    def click_footer_customer_service(self):
        """點擊頁尾「客服中心」連結。"""
        self.click_element_safely(self.FOOTER_CS_LINK)