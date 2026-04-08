from selenium.webdriver.common.by import By
from .base_page import BasePage

class PortalPage(BasePage):
    # 💡 更新定位器：根據截圖，將 'gama' 改成 'bf' 來鎖定新版登入口
    NEW_BF_LOGIN_BTN = (By.XPATH, "//a[contains(@class, 'btn') and (contains(., 'beanfun') or contains(., '登入'))]")

    def click_gama_portal(self):
        print("正在嘗試點擊新版 Beanfun 登入口...")
        try:
            # 🟢 改用 js_click 繞過 ElementClickIntercepted 錯誤
            self.js_click(self.NEW_BF_LOGIN_BTN)
            print("✅ 成功使用 JS 強制點擊登入口")
        except Exception as e:
            print(f"❌ 連 JS 點擊都失敗: {e}")
            raise e