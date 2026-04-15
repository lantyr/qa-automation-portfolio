from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage
import os

class HomePage(BasePage):
    # ════════════════════════════════════════════════
    # 定位器 (Locators) - 確保命名與呼叫一致
    # ════════════════════════════════════════════════
    LOGO = (By.CSS_SELECTOR, "a.logo.oneBrand.bilingual")
    
    # --- Banner 區塊 ---
    # 大看板 iframe（主文件 context，無 id，以 class 定位）
    BANNER_IFRAME    = (By.CSS_SELECTOR, "iframe.banner")
    # 以下定位器須在切換至 BANNER_IFRAME context 後使用
    BANNER_CONTAINER = (By.CSS_SELECTOR, "ul.bxslider")
    ACTIVE_BANNER_LINK = (By.CSS_SELECTOR, "ul.bxslider li.pic:not([style*='display: none']) a.pic")
    # 切換按鈕在主文件 context（不在 iframe 內）
    BANNER_PREV_BTN  = (By.CSS_SELECTOR, "div.slider-l")
    BANNER_NEXT_BTN  = (By.CSS_SELECTOR, "div.slider-r")
    
    # --- 最新消息區塊 ---
    NEWS_CONTAINER = (By.CSS_SELECTOR, "div.newsitem")
    NEWS_LIST_ITEMS = (By.CSS_SELECTOR, "div.newsitem ul li") # ⚠️ 原腳本缺失
    NEWS_FIRST_ITEM_LINK = (By.CSS_SELECTOR, "div.newsitem ul li:nth-child(1) a")
    NEWS_FIRST_ITEM_TXT = (By.CSS_SELECTOR, "div.newsitem ul li:nth-child(1) a span.txt")
    
    # --- Chatbot 區塊 ---
    CHATBOT_BTN = (By.ID, "gim-bot-tool-button")
    CHATBOT_WINDOW_TITLE = (By.XPATH, "//h3[contains(text(), '遊戲橘子客服小幫手')]")

    # --- 登入 / 登出 ---
    LOGIN_BTN  = (By.ID, "BF_anchorLoginBtn")
    LOGOUT_BTN = (By.ID, "BF_btnLogout")

    # --- 右側導覽列按鈕（BF_divRightButtons） ---
    SIGNUP_BTN = (By.ID, "BF_btnSignup")   # 申請帳號
    MEMBER_BTN = (By.ID, "BF_btnMember")   # 會員中心
    BAG_BTN    = (By.ID, "BF_btnBag")      # 雲端背包
    OPEN_BTN   = (By.ID, "BF_btnOpen")     # 開通服務
    MISSION_DASHBOARD_FORM = (By.CSS_SELECTOR, "form#form1[action='MissionDashBoard.aspx']")

    # --- 剩餘點數數字 ---
    REMAIN_POINT = (By.ID, "BF_RemainPoint")

    # --- 快速啟動遊戲 ---
    QUICK_START_BTN = (By.ID, "BF_btnQuickStart")

    # --- 快速啟動彈窗（BF_divPopWindow）---
    # 點擊 BF_btnQuickStart 後出現
    QUICK_START_POPUP   = (By.ID, "BF_divPopWindow")
    # 彈窗內遊戲清單第一個 <li>（onclick="BeanFunBlock.StartGameWithAccountData(...)"）
    QUICK_START_GAME_LI = (By.CSS_SELECTOR, "#BF_BaseList li")

    # --- GASH 點數子選單 ---
    # BF_btnGash：右下角「我的錢包/儲值」按鈕，點擊後展開 BF_divGashSubMenu
    REMAINING_POINTS_TOGGLE = (By.ID, "BF_btnGash")
    GASH_SUBMENU             = (By.ID, "BF_divGashSubMenu")
    TOPUP_PURCHASE_LINK      = (By.XPATH,
        "//*[@id='BF_divGashSubMenu']//li[contains(.,'儲值與購點')]"
    )
    YOUTUBE_IFRAME = (By.XPATH, "//iframe[contains(@src, 'youtube')]")
    YT_LARGE_PLAY_BTN = (By.CSS_SELECTOR, "button.ytmCuedOverlayPlayButton, button.ytp-large-play-button")
    # --- 導覽列狀態驗證 ---
    def assert_logged_out_navbar(self) -> None:
        """驗證未登入狀態：登入、申請帳號、我的錢包、會員中心 可見；登出 不可見。"""
        assert self.is_element_displayed(self.LOGIN_BTN), "登入按鈕應可見"
        assert self.is_element_displayed(self.SIGNUP_BTN), "申請帳號應可見"
        assert self.is_element_displayed(self.REMAINING_POINTS_TOGGLE), "我的錢包應可見"
        assert self.is_element_displayed(self.MEMBER_BTN), "會員中心應可見"
        assert not self.is_element_displayed(self.LOGOUT_BTN, timeout=3), "登出不應可見"

    def assert_logged_in_navbar(self, has_bag: bool = False) -> None:
        """驗證已登入狀態：登出、剩餘點數、會員中心、開通服務 可見；has_bag 控制是否驗證雲端背包。"""
        assert self.is_element_displayed(self.LOGOUT_BTN), "登出應可見"
        assert self.is_element_displayed(self.REMAINING_POINTS_TOGGLE), "剩餘點數應可見"
        assert self.is_element_displayed(self.MEMBER_BTN), "會員中心應可見"
        assert self.is_element_displayed(self.OPEN_BTN), "開通服務應可見"
        if has_bag:
            assert self.is_element_displayed(self.BAG_BTN), "雲端背包應可見"
        else:
            assert not self.is_element_displayed(self.BAG_BTN, timeout=3), "雲端背包不應可見"

    # --- 頁尾連結 ---
    # footer.js 產生 <div id="divFooter">，CS 連結 href 指向 csp.beanfun.com
    FOOTER_CS_LINK = (By.CSS_SELECTOR, "#divFooter a[href*='csp.beanfun.com']")
    def scroll_to_youtube_video(self):
        """捲動至 YouTube 影片 iframe (嚴守 Rule 6: 避免 JS，使用 ActionChains)"""
        iframe_el = self.wait.until(EC.presence_of_element_located(self.YOUTUBE_IFRAME))
        ActionChains(self.driver).scroll_to_element(iframe_el).perform()
        return self.wait_until_visible(self.YOUTUBE_IFRAME)

    def play_youtube_video(self):
        """切換至 iframe 並點擊影片大播放鍵"""
        self.scroll_to_youtube_video()
        iframe_el = self.wait_until_visible(self.YOUTUBE_IFRAME)
        
        # 必須切換 context 才能操作 iframe 內的元素
        self.driver.switch_to.frame(iframe_el)
        try:
            print("👉 嘗試點擊 YouTube 播放按鈕...")
            # 使用你 BasePage 封裝的安全點擊 (忽略遮擋與 Stale)
            self.click_element_safely(self.YT_LARGE_PLAY_BTN)
        finally:
            # 💡 確保無論點擊是否發生異常，都強制切回主畫面，防止污染後續測試 (Rule 8)
            self.driver.switch_to.default_content()

    def verify_youtube_is_playing(self):
        """斷言驗證：大型播放鍵消失"""
        iframe_el = self.wait_until_visible(self.YOUTUBE_IFRAME)
        self.driver.switch_to.frame(iframe_el)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(self.YT_LARGE_PLAY_BTN)
            )
            return True
        except Exception as e:
            raise AssertionError(f"FAIL: 點擊後播放按鈕依然存在，影片未能執行。細節: {e}")
        finally:
            self.driver.switch_to.default_content()
    def __init__(self, driver):
        super().__init__(driver)
        # 從環境變數讀取，若無則給予預設值 (遵守 Rule 8)
        self.url = os.getenv("BASE_URL", "https://tw.beanfun.com/")

    # ════════════════════════════════════════════════
    # 頁面行為 (Page Actions) - 統一依賴 BasePage 的封裝
    # ════════════════════════════════════════════════
    def go_to_home(self):
        """導航至首頁並等待 LOGO 出現，若頁面回傳 429 則標記為被鎖定。"""
        self.driver.get(self.url)
        self.check_for_rate_limit()
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
        self.click_element_safely(self.CHATBOT_BTN)

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
            # 開通 Gama Pass 廣告彈窗的 X 按鈕（登入後可能出現）
            (By.XPATH, "//*[contains(@class,'close') or @aria-label='Close' or @aria-label='關閉']"),
            (By.XPATH, "//button[@type='button'][contains(@class,'close') or contains(@class,'btn-close')]"),
            (By.CSS_SELECTOR, "[class*='modal'] [class*='close'], [class*='popup'] [class*='close']"),
        ]
        for locator in close_patterns:
            try:
                for el in self.driver.find_elements(*locator):
                    if el.is_displayed():
                        el.click()
            except Exception:
                pass

    def click_quick_start(self):
        """點擊快速啟動遊戲按鈕（BF_btnQuickStart），觸發彈窗出現。"""
        self.click_element_safely(self.QUICK_START_BTN)

    def click_first_game_in_popup(self):
        """點擊快速啟動彈窗中第一個遊戲 li，觸發 StartGameWithAccountData。"""
        self.click_element_safely(self.QUICK_START_GAME_LI)

    def click_member_center(self):
        """點擊會員中心按鈕，觸發頁面跳轉。"""
        self.click_element_safely(self.MEMBER_BTN)

    # --- 儲值與購點 Actions ---
    def open_topup_popup(self):
        """
        展開 GASH 點數子選單，再點擊「儲值與購點」進入彈窗。
        若選單已展開（toggle 狀態殘留），直接使用；若未展開才點擊開啟。
        點擊後等待 JS alert（資安提示）出現並接受，最多等 5 秒。
        """
        if not self.is_element_displayed(self.GASH_SUBMENU, timeout=2):
            self.click_element_safely(self.REMAINING_POINTS_TOGGLE)
        self.wait_until_visible(self.GASH_SUBMENU)
        self.click_element_safely(self.TOPUP_PURCHASE_LINK)
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except TimeoutException:
            pass

    def click_bag_btn(self):
        """點擊雲端背包按鈕，會開新分頁。"""
        self.click_element_safely(self.BAG_BTN)

    def click_open_service(self):
        """點擊開通服務按鈕，展開 fbContent 彈窗。"""
        from selenium.webdriver.support import expected_conditions as EC_inner
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.common.exceptions import TimeoutException
        self.click_element_safely(self.OPEN_BTN)
        try:
            WebDriverWait(self.driver, 5).until(EC_inner.alert_is_present())
            self.driver.switch_to.alert.accept()
        except TimeoutException:
            pass

    # --- 頁尾 Actions ---
    def scroll_to_footer(self):
        """捲動至頁面底部使頁尾連結可見。"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.wait_until_visible(self.FOOTER_CS_LINK)

    def click_footer_customer_service(self):
        """點擊頁尾「客服中心」連結。"""
        self.click_element_safely(self.FOOTER_CS_LINK)