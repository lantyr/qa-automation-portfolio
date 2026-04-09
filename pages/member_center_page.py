"""
Page Object for 會員中心（Member Center）popup。

結構：點擊 BF_btnMember → fbContent iframe 彈窗出現
      iframe 內有 div.memberList 側欄，含四個可展開大分類。
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage


class MemberCenterPage(BasePage):

    # ── Popup ────────────────────────────────────────────────────
    POPUP_ROOT = (By.ID, "fbContent")

    # ── 側欄容器 ─────────────────────────────────────────────────
    MEMBER_LIST = (By.CSS_SELECTOR, "div.memberList")

    # ── 大分類標題（點擊展開/收合）────────────────────────────────
    CAT_MEMBER_INFO   = (By.CSS_SELECTOR, "a.memberItemTitle.targetBtn[data-page='1']")
    CAT_SERVICE_OPEN  = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(.,'服務開通')]")
    CAT_QUERY_RECORDS = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(.,'查詢紀錄')]")
    CAT_MEMBER_NOTICE = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(.,'會員須知')]")

    # ── 展開後 active 狀態（含 active class）──────────────────────
    CAT_SERVICE_OPEN_ACTIVE  = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(@class,'active') and contains(.,'服務開通')]")
    CAT_QUERY_RECORDS_ACTIVE = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(@class,'active') and contains(.,'查詢紀錄')]")
    CAT_MEMBER_NOTICE_ACTIVE = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(@class,'active') and contains(.,'會員須知')]")

    # ── 子項目（data-page 對照）──────────────────────────────────
    SUB_OPEN_BENEFIT  = (By.CSS_SELECTOR, "div.targetBtn[data-page='3']")   # 開通權益
    SUB_EMAIL         = (By.CSS_SELECTOR, "div.targetBtn[data-page='4']")   # 取消/訂閱電子報
    SUB_SMS           = (By.CSS_SELECTOR, "div.targetBtn[data-page='5']")   # 取消/訂閱簡訊
    SUB_ACCOUNT_LOG   = (By.CSS_SELECTOR, "div.targetBtn[data-page='6']")   # 帳號大事紀
    SUB_GAME_LOG      = (By.CSS_SELECTOR, "div.targetBtn[data-page='7']")   # 遊戲使用紀錄
    SUB_GAME_UNLOCK   = (By.CSS_SELECTOR, "div.targetBtn[data-page='8']")   # 遊戲帳號解鎖專區
    SUB_SMS_OTP       = (By.CSS_SELECTOR, "div.targetBtn[data-page='9']")   # 簡訊OTP驗證專區
    SUB_TERMS         = (By.CSS_SELECTOR, "div.targetBtn[data-page='10']")  # 服務條款
    SUB_GUIDE         = (By.CSS_SELECTOR, "div.targetBtn[data-page='11']")  # 新手引導
    SUB_MEMBER_CERT   = (By.CSS_SELECTOR, "div.targetBtn[data-page='12']")  # 會員認證

    # ── 方法 ─────────────────────────────────────────────────────

    def assert_popup_visible(self, timeout: int = 10) -> None:
        """驗證 fbContent 彈窗出現。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.POPUP_ROOT)
        )

    def switch_to_iframe(self, timeout: int = 10) -> None:
        """切換至 fbContent iframe context。"""
        iframe = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.POPUP_ROOT)
        )
        self.driver.switch_to.frame(iframe)

    def assert_member_list_visible(self, timeout: int = 10) -> None:
        """驗證側欄大分類列表可見。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.MEMBER_LIST)
        )

    def click_category(self, locator, timeout: int = 10) -> None:
        """點擊大分類（展開/收合）。"""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        ).click()

    def assert_category_expanded(self, active_locator, timeout: int = 10) -> None:
        """驗證大分類已展開（drawerBtn 含 active class）。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(active_locator)
        )

    def click_sub_item(self, locator, timeout: int = 10) -> None:
        """點擊子項目。"""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        ).click()

    def assert_sub_item_active(self, data_page: str, timeout: int = 10) -> None:
        """驗證子項目已選取（targetBtn 含 active class）。"""
        locator = (By.CSS_SELECTOR, f"div.targetBtn.active[data-page='{data_page}']")
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
