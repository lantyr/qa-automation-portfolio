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

    # ── 關閉按鈕（主文件 context，位於彈窗右上角）───────────
    # default.css: #BF_divPopWindow .BF_Header .BF_CloseButton a.popclose
    CLOSE_BTN = (By.ID, "fbClose")

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
    CURRENT_POINTS_AREA   = (By.ID, "Remain_point1_lbl_remain_point")

    # ── 左側導覽列（iframe context 內）─────────────────────
    # ⚠️ 需依實際 DOM 調整
    NAV_BUY_POINTS   = (By.XPATH, "//div[contains(@class,'menuButton') and contains(.,'購買點數')]")
    NAV_TOPUP_RECORD = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'儲值記錄')]")
    NAV_CONSUMPTION  = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'消費記錄')]")
    NAV_GAME_POINTS  = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'遊戲專用點數')]")
    NAV_RECENT_TOPUP = (By.XPATH, "//a[contains(@class,'leftMenuSub') and contains(.,'最近的儲值紀錄')]")
    NAV_BILLING      = (By.XPATH, "//div[contains(@class,'menuButton') and contains(.,'計費設定')]")

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

    def assert_current_points_visible(self, timeout: int = 10) -> None:
        """驗證左側帳號資訊區「當前點數」可見。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.CURRENT_POINTS_AREA)
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

    def click_close_button(self, timeout: int = 10) -> None:
        """切換回主文件後點擊關閉按鈕，並等待彈窗消失。"""
        self.driver.switch_to.default_content()
        self.click_element_safely(self.CLOSE_BTN)
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(self.POPUP_ROOT)
        )
