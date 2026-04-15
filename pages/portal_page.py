from selenium.webdriver.common.by import By
from .base_page import BasePage


class PortalPage(BasePage):

    BF_LOGIN_BTN = (
        By.XPATH,
        "//a[contains(@class, 'btn') and (contains(., 'beanfun') or contains(., '登入'))]",
    )

    def click_bf_login(self):
        """點擊 Portal 頁面的 beanfun 登入選項。"""
        self.click_element_safely(self.BF_LOGIN_BTN)

    # 向下相容：舊名稱保留
    NEW_BF_LOGIN_BTN = BF_LOGIN_BTN

    def click_gama_portal(self):
        """舊方法名，保留向下相容。"""
        self.click_bf_login()