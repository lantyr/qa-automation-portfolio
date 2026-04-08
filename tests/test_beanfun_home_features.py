import pytest
from pages.home_page import HomePage

@pytest.mark.usefixtures("driver") # 假設你在 conftest.py 有設定 driver fixture
class TestBeanfunHomeFeatures:
    
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        """Rule 8: 每次測試前初始化 HomePage 並前往首頁，確保狀態隔離"""
        self.home_page = HomePage(driver)
        self.home_page.go_to_home()

    def test_home_page_render_tc001(self):
        """
        1. 測試編號: TC_HOME_001
        2. 測試標題: 驗證首頁渲染與網頁 Title 顯示正常
        3. 測試步驟:
           - 前往遊戲橘子首頁
           - 取得當前網頁 Title
        4. 預期結果: 顯示正常，Title 為「遊戲橘子」
        """
        title = self.home_page.get_page_title()
        assert "遊戲橘子" in title, f"預期 Title 包含'遊戲橘子'，實際為: {title}"


    

    def test_chatbot_functionality_tc002(self):
        """
        1. 測試編號: TC_HOME_004
        2. 測試標題: 驗證右下角 Chatbot 浮水印顯示與點擊
        3. 測試步驟:
           - 檢查浮水印顯示
           - 點擊浮水印
        4. 預期結果: 顯示正常、點擊正常不報錯
        """
        assert self.home_page.verify_chatbot_ready() is not False, "Chatbot 圖示未顯示"
        self.home_page.click_chatbot()
        # 若有對話框彈出，可在此處補充 assert_element_visible(對話框 Locator)