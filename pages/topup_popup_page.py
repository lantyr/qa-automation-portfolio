"""
Page Object for 儲值與購點 (Top-up & Purchase Points) popup.

彈窗結構：
  主文件 → 點擊 GASH 子選單 → 彈窗出現 (fbContent 為根容器)
           → 彈窗內含 iframe (功能操作區域)
           → iframe 內有左側帳號資訊、左側導覽列、右側頁面內容

⚠️ 所有定位器均依 beanfun 慣用命名與 TC 描述推定，
   實際 DOM 可能有差異，請以 DevTools 核對後調整。
"""
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage


class TopupPopupPage(BasePage):

    # ════════════════════════════════════════════════
    # 定位器 (Locators)
    # ════════════════════════════════════════════════

    # ── 彈窗根容器（主文件 context）─────────────────────────
    # floatbox 產生 id="fbContent" 作為彈窗內容容器
    POPUP_ROOT = (By.ID, "fbContent")

    # ── 彈窗內部 iframe（功能操作區域）──────────────────────
    # 彈窗本身即為 iframe，id="fbContent"
    POPUP_IFRAME = (By.ID, "fbContent")

    # ── 內容區 iframe（購買點數、序號儲值等頁面載入在此）────
    # src="point_buy_default.aspx" 等，name="beanfun_main_content"
    CONTENT_IFRAME = (By.NAME, "beanfun_main_content")

    # ── 關閉按鈕（主文件 context，位於彈窗右上角）───────────
    # default.css: #BF_divPopWindow .BF_Header .BF_CloseButton a.popclose
    # 定位實際可點擊的 <a> 連結，而非外層容器 div#fbClose
    CLOSE_BTN = (By.CSS_SELECTOR, "a.popclose")

    # ── 防詐騙 OTP 驗證彈窗（iframe context 內，可能出現）───
    # ⚠️ 需依實際 DOM 調整
    ANTI_FRAUD_MODAL = (By.XPATH,
        "//*[contains(@class,'fraud') or contains(@class,'otp-verify') "
        "    or contains(text(),'防詐騙')]"
    )
    ANTI_FRAUD_CONFIRM = (By.XPATH,
        "//button[contains(.,'我知道了') or contains(.,'確認') or contains(.,'關閉')]"
    )

    # ── 左側帳號資訊區（iframe context 內）─────────────────
    # ⚠️ 需依實際 DOM 調整
    REMAINING_POINTS_AREA = (By.ID, "Remain_point1_lbl_remain_point")
    MEMBER_VERIFIED_LABEL = (By.ID, "Remain_point1_lblVerifiedMember")
    CURRENT_POINTS_AREA   = (By.ID, "Remain_point1_lbl_remain_point")

    # ── 左側導覽列（iframe context 內）─────────────────────
    # ⚠️ 需依實際 DOM 調整
    NAV_QUERY_RECORDS = (By.XPATH, "//div[contains(@class,'menuButton') and contains(.,'查詢記錄')]")
    NAV_BUY_POINTS   = (By.XPATH, "//div[contains(@class,'menuButton') and contains(.,'購買點數')]")
    NAV_TOPUP_RECORD = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'儲值記錄')]")
    NAV_CONSUMPTION  = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'消費記錄')]")
    NAV_GAME_POINTS  = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'遊戲專用點數')]")
    NAV_RECENT_TOPUP = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'最近的儲值紀錄')]")
    NAV_BILLING      = (By.XPATH, "//div[contains(@class,'menuButton') and contains(.,'計費設定')]")
    NAV_SERIAL_TOPUP  = (By.XPATH, "//div[contains(@class,'menuButton') and contains(.,'序號儲值')]")
    LOCKED_BUY_VERIFY_BTN    = (By.CSS_SELECTOR, "a.btn.active")   # SP-013 購買點數未解鎖：onclick="goVerification()"
    LOCKED_SERIAL_VERIFY_BTN = (By.ID, "lnkAdvancedVerify")        # SP-014 序號儲值未解鎖：無 active class
    BUY_POINTS_GBOX_BTN      = (By.CSS_SELECTOR, "div.gbox-action a.gbox-btn")  # 未解鎖的前往驗證按鈕
    PAYMENT_TYPE_BTNS        = (By.CSS_SELECTOR, "div.type-btns")               # SP-015 已解鎖：支付方式選擇容器

    # ── 頁面內容載入指標（iframe context 內）────────────────
    # 點擊左側導覽後等待此元素出現代表主內容已載入
    # ⚠️ 需依實際 DOM 調整
    PAGE_CONTENT = (By.XPATH,
        "//div[@id='content'] | //div[contains(@class,'main')] | "
        "//table | //ul[contains(@class,'list')]"
    )

    # ════════════════════════════════════════════════
    # 頁面行為 (Page Actions)
    # ════════════════════════════════════════════════

    def assert_popup_root_visible(self, timeout: int = 10) -> None:
        """驗證彈窗根容器 (fbContent) 已存在且可見。"""
        self.wait_until_visible(self.POPUP_ROOT)

    def switch_to_popup_iframe(self, timeout: int = 10) -> None:
        """切換至彈窗內的功能操作 iframe。"""
        self.driver.switch_to.default_content()
        iframe = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.POPUP_IFRAME)
        )
        self.driver.switch_to.frame(iframe)

    def switch_to_content_iframe(self, timeout: int = 10) -> None:
        """切換至彈窗內的內容 iframe（beanfun_main_content）。
        須在已切換至 POPUP_IFRAME (fbContent) 後呼叫。"""
        iframe = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.CONTENT_IFRAME)
        )
        self.driver.switch_to.frame(iframe)

    def switch_to_default(self) -> None:
        """切換回主文件 context。"""
        self.driver.switch_to.default_content()

    def dismiss_anti_fraud_if_present(self, timeout: int = 5) -> None:
        """
        偵測防詐騙 OTP 驗證彈窗，若出現則關閉。
        彈窗出現與否均屬系統預期行為，兩者均繼續執行測試。
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.ANTI_FRAUD_MODAL)
            )
            self.click_element_safely(self.ANTI_FRAUD_CONFIRM)
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.ANTI_FRAUD_MODAL)
            )
        except TimeoutException:
            pass  # 彈窗未出現，屬正常，繼續執行

    def assert_remaining_points_visible(self, timeout: int = 10) -> None:
        """驗證左側帳號資訊區「剩餘點數」可見。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.REMAINING_POINTS_AREA)
        )

    def assert_verified_member(self, timeout: int = 10) -> None:
        """驗證側欄顯示「認證會員」（有進階認證）。"""
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.MEMBER_VERIFIED_LABEL)
        )
        assert '認證會員' in el.text, f'預期顯示認證會員，實際為：{el.text}'

    def assert_general_member(self, timeout: int = 10) -> None:
        """驗證側欄顯示「一般會員」（無進階認證）。"""
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.MEMBER_VERIFIED_LABEL)
        )
        assert '一般會員' in el.text, f'預期顯示一般會員，實際為：{el.text}'

    def get_member_verified_text(self, timeout: int = 10) -> str:
        """取得側欄會員認證狀態文字。"""
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.MEMBER_VERIFIED_LABEL)
        )
        return el.text.strip()

    def assert_current_points_visible(self, timeout: int = 10) -> None:
        """驗證左側帳號資訊區「當前點數」可見。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.CURRENT_POINTS_AREA)
        )

    def expand_query_records(self, timeout: int = 10) -> None:
        """
        確保「查詢記錄」子選單已展開（含 'open' class）。
        若已展開則不重複點擊，避免收合。
        """
        btn = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.NAV_QUERY_RECORDS)
        )
        if "open" not in btn.get_attribute("class"):
            btn.click()
        # 等待子選單項目可見
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.NAV_TOPUP_RECORD)
        )

    def click_nav_item(self, locator) -> None:
        """點擊左側導覽列指定項目，並處理可能出現的 JS alert。"""
        self.click_element_safely(locator)
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
            self.switch_to_popup_iframe()
        except TimeoutException:
            pass

    def assert_page_content_loaded(self, timeout: int = 10) -> None:
        """驗證點擊導覽後右側頁面主要內容已載入。"""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.PAGE_CONTENT)
        )

    def assert_buy_points_locked(self, timeout: int = 10) -> None:
        """SP-013：購買點數頁未解鎖，切換至內層 iframe 後驗證「前往認證」按鈕（a.btn.active）存在。"""
        self.switch_to_content_iframe(timeout)
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.LOCKED_BUY_VERIFY_BTN)
        )
        assert "前往認證" in el.text, f"預期顯示前往認證按鈕，實際文字：{el.text}"

    def assert_serial_topup_locked(self, timeout: int = 10) -> None:
        """SP-014：序號儲值頁未解鎖，切換至內層 iframe 後驗證「前往認證」連結（#lnkAdvancedVerify）存在。"""
        self.switch_to_content_iframe(timeout)
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.LOCKED_SERIAL_VERIFY_BTN)
        )
        assert "前往認證" in el.text, f"預期顯示前往認證連結，實際文字：{el.text}"

    def assert_buy_points_unlocked(self, timeout: int = 10) -> None:
        """SP-015：切換至內層 iframe，驗證支付方式選擇容器（div.type-btns）可見。"""
        self.switch_to_content_iframe(timeout)
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.PAYMENT_TYPE_BTNS)
        )

    def click_nav_serial_topup(self, timeout: int = 10) -> None:
        """點擊左側導覽「序號儲值」，並處理可能出現的 JS alert 後重新切回 iframe。"""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.NAV_SERIAL_TOPUP)
        ).click()
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
            self.switch_to_popup_iframe(timeout)
        except TimeoutException:
            pass

    def click_nav_buy_points(self, timeout: int = 10) -> None:
        """點擊左側導覽「購買點數」，並處理可能出現的 JS alert 後重新切回 iframe。"""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.NAV_BUY_POINTS)
        ).click()
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
            self.switch_to_popup_iframe(timeout)
        except TimeoutException:
            pass

    def click_close_button(self, timeout: int = 10) -> None:
        """切換回主文件後點擊關閉按鈕，並等待彈窗消失。"""
        self.driver.switch_to.default_content()
        self.click_element_safely(self.CLOSE_BTN)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(self.POPUP_ROOT)
        )
