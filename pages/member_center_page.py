"""
Page Object for 會員中心（Member Center）popup。

結構：點擊 BF_btnMember → fbContent iframe 彈窗出現
      iframe 內有 div.memberList 側欄，含導覽分類。

DOM 結構（依 DevTools 確認）：
  div.memberList
    div.memberItem
      a.memberItemTitle.targetBtn[data-page='1']  ← 會員資料（直接連結）
    div.memberItem
      a.memberItemTitle.targetBtn[data-page='2']  ← 帳號整合（星帳專屬）
    div.memberItem
      div.memberItemTitle.drawerBtn               ← 服務開通（展開後 class 加 'open'）
      div.drawer[style="display:block"]           ← 展開時 display:block
        div.targetBtn[data-page='3']              ← 開通權益
        div.targetBtn[data-page='4']              ← 取消/訂閱電子報
        div.targetBtn[data-page='5']              ← 取消/訂閱簡訊
    div.memberItem
      div.memberItemTitle.drawerBtn               ← 查詢紀錄
      div.drawer
        div.targetBtn[data-page='6']              ← 帳號大事紀
        div.targetBtn[data-page='7']              ← 遊戲使用紀錄
        div.targetBtn[data-page='8']              ← 遊戲帳號解鎖專區
        div.targetBtn[data-page='9']              ← 簡訊OTP驗證專區
    div.memberItem
      div.memberItemTitle.drawerBtn               ← 會員須知
      div.drawer
        div.targetBtn[data-page='10']             ← 服務條款
        div.targetBtn[data-page='11']             ← 新手引導
        div.targetBtn[data-page='12']             ← 會員認證
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

    # ── 大分類：直接連結型 ────────────────────────────────────────
    CAT_MEMBER_INFO         = (By.CSS_SELECTOR, "a.memberItemTitle.targetBtn[data-page='1']")  # 會員資料
    CAT_ACCOUNT_INTEGRATION = (By.CSS_SELECTOR, "a.memberItemTitle.targetBtn[data-page='2']")  # 帳號整合（星帳專屬）

    # ── 大分類：Drawer 展開型 ─────────────────────────────────────
    CAT_SERVICE_OPEN  = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(.,'服務開通')]")
    CAT_QUERY_RECORDS = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(.,'查詢紀錄')]")
    CAT_MEMBER_NOTICE = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(.,'會員須知')]")

    # ── Drawer 已展開狀態（class 加 'open'，DevTools 確認）────────
    CAT_SERVICE_OPEN_EXPANDED  = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(@class,'open') and contains(.,'服務開通')]")
    CAT_QUERY_RECORDS_EXPANDED = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(@class,'open') and contains(.,'查詢紀錄')]")
    CAT_MEMBER_NOTICE_EXPANDED = (By.XPATH, "//div[contains(@class,'drawerBtn') and contains(@class,'open') and contains(.,'會員須知')]")

    # ── 服務開通 子項目（data-page 3~5）──────────────────────────
    SUB_OPEN_BENEFIT = (By.CSS_SELECTOR, "div.targetBtn[data-page='3']")   # 開通權益
    SUB_EMAIL        = (By.CSS_SELECTOR, "div.targetBtn[data-page='4']")   # 取消/訂閱電子報
    SUB_SMS          = (By.CSS_SELECTOR, "div.targetBtn[data-page='5']")   # 取消/訂閱簡訊

    # ── 查詢紀錄 子項目（data-page 6~9）──────────────────────────
    SUB_ACCOUNT_LOG = (By.CSS_SELECTOR, "div.targetBtn[data-page='6']")    # 帳號大事紀
    SUB_GAME_LOG    = (By.CSS_SELECTOR, "div.targetBtn[data-page='7']")    # 遊戲使用紀錄
    SUB_GAME_UNLOCK = (By.CSS_SELECTOR, "div.targetBtn[data-page='8']")    # 遊戲帳號解鎖專區
    SUB_SMS_OTP     = (By.CSS_SELECTOR, "div.targetBtn[data-page='9']")    # 簡訊OTP驗證專區

    # ── 會員須知 子項目（data-page 10~12）────────────────────────
    SUB_TERMS       = (By.CSS_SELECTOR, "div.targetBtn[data-page='10']")   # 服務條款
    SUB_GUIDE       = (By.CSS_SELECTOR, "div.targetBtn[data-page='11']")   # 新手引導
    SUB_MEMBER_CERT = (By.CSS_SELECTOR, "div.targetBtn[data-page='12']")   # 會員認證

    # ── 帳號資訊區（依 DevTools 確認）
    REMAINING_POINTS_AREA = (By.ID, "remainPointDisplay")
    REFRESH_POINTS_BTN    = (By.CSS_SELECTOR, "svg-wrap[onclick='updateRemainPoint()']")

    # ════════════════════════════════════════════════════════════
    # 方法
    # ════════════════════════════════════════════════════════════

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
        """驗證側欄大分類列表容器可見。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.MEMBER_LIST)
        )

    def assert_remaining_points_visible(self, timeout: int = 10) -> None:
        """驗證左側點數區可見。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.REMAINING_POINTS_AREA)
        )

    def click_refresh_points(self, timeout: int = 10) -> None:
        """點擊「更新點數」按鈕。"""
        btn = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.REFRESH_POINTS_BTN)
        )
        btn.click()

    def click_category(self, locator, timeout: int = 10) -> None:
        """點擊大分類（展開/收合 或 直接連結）。"""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        ).click()

    def assert_category_visible(self, locator, timeout: int = 10) -> None:
        """驗證大分類項目可見。"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def assert_drawer_expanded(self, expanded_locator, timeout: int = 10) -> None:
        """驗證 drawer 已展開（drawerBtn 含 'open' class）。"""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(expanded_locator)
        )

    def assert_sub_items_visible(self, *locators, timeout: int = 10) -> None:
        """驗證多個子項目在 drawer 展開後均可見。"""
        for loc in locators:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(loc)
            )

    def click_sub_item(self, locator, timeout: int = 10) -> None:
        """點擊 drawer 內子項目。"""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        ).click()

    def assert_target_active(self, data_page: str, timeout: int = 10) -> None:
        """驗證指定 targetBtn 已被選取（含 active class）→ 右側頁面已切換。"""
        locator = (By.CSS_SELECTOR, f"[data-page='{data_page}'].active")
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
