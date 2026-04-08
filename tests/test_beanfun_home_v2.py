import json
from pathlib import Path
import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 關鍵修正：確保所有 Page Classes 都有被匯入
from config.credentials import get_beanfun_otp, require_beanfun_credentials
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.portal_page import PortalPage

_DATA_FILE = Path(__file__).parent / "data" / "home_test_data.json"
with open(_DATA_FILE, encoding="utf-8") as _f:
    TEST_DATA = json.load(_f)

@allure.feature("PC版官網首頁")
@pytest.mark.usefixtures("class_driver")
class TestBeanfunHomeV2:

    @pytest.fixture(autouse=True)
    def _setup_pages(self, request, class_driver):
        """
        利用 request.cls 將 Page Objects 注入到測試類別實例中。
        """
        request.cls.driver = class_driver
        request.cls.home = HomePage(class_driver)
        request.cls.login_page = LoginPage(class_driver) # 修正點：LoginPage 現在已定義
        request.cls.portal = PortalPage(class_driver)
        request.cls.timeout = TEST_DATA.get("element_timeout", 10)
        
        # 嚴格遵守 Rule 5：移除所有隱式等待
        class_driver.implicitly_wait(0) 

    # ════════════════════════════════════════════════
    # 一、 基礎渲染與未登入狀態驗證
    # ════════════════════════════════════════════════

    """
    Test ID: BF-HOME-01
    Test Title: 1-3. 驗證網站標題、網址與 LOGO
    Test Steps:
        1. 呼叫 go_to_home() 進入官網並等待核心元件載入。
        2. 驗證 driver.title 是否包含「遊戲橘子」。
        3. 驗證目前 URL 是否符合 TEST_DATA 預期。
        4. 驗證 LOGO 元件是否於超時內可見且可點擊。
    Expected Result: 頁面成功加載，標題、URL 與 LOGO 均符合規格。
    """
    @allure.title("10-12. 驗證中段遊戲分類頁籤切換")
    def test_04_verify_game_tabs(self):
        with allure.step("10. 驗證「熱門線上遊戲」頁籤"):
            self.home.assert_element_ready(HomePage.TAB_HOT_ONLINE, self.timeout).click()
            self.home.assert_element_visible(HomePage.LIST_HOT_ONLINE, self.timeout)

        with allure.step("11. 驗證「超人氣手機遊戲」頁籤"):
            self.home.assert_element_ready(HomePage.TAB_POPULAR_MOBILE, self.timeout).click()
            self.home.assert_element_visible(HomePage.LIST_POPULAR_MOBILE, self.timeout)

        with allure.step("12. 驗證「原廠直營遊戲」頁籤"):
            self.home.assert_element_ready(HomePage.TAB_DIRECT_OPERATED, self.timeout).click()
            self.home.assert_element_visible(HomePage.LIST_DIRECT_OPERATED, self.timeout)

    """
    Test ID: BF-HOME-13-15
    Test Title: 驗證廣告看板與 YouTube 影音播放
    Test Steps:
        1. 驗證中段廣告看板 (如：天堂M) 是否存在。
        2. 滾動至影音區塊，切換至 YouTube Iframe。
        3. 執行原生 click() 觸發播放。
    Expected Result: 廣告圖載入正常，YouTube 影片可被觸發點擊。
    """
    @allure.title("13-15. 驗證中段廣告圖與 YouTube 影音區塊")
    def test_05_verify_mid_ads_and_video(self):
        with allure.step("13. 驗證中段廣告看板"):
            self.home.assert_element_visible(HomePage.MID_AD_BANNER, self.timeout)
            
        with allure.step("14-15. 驗證 YouTube 影音播放"):
            # 嚴格遵守 Rule 6：禁止使用 JS 注入點擊播放按鈕
            self.home.switch_to_youtube_and_play(self.timeout)