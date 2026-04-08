import pytest
from pages.home_page import HomePage

class TestHomepageSmoke:
    
    @pytest.fixture(autouse=True)
    def setup_class(self, driver):
        self.home_page = HomePage(driver)
        self.home_page.open_homepage() 

    def test_hero_banner_smoke(self):
        """
        Test ID: SMOKE_001
        Title: 驗證首頁大看板顯示、連結與切換功能
        Steps:
           1. 進入首頁
           2. 檢查大看板 IFrame 是否顯示
           3. 點擊看板切換按鈕 (Next)
           4. 點擊當前看板連結
        Result: 成功開啟新分頁
        """
        # 1. 驗證大看板顯示
        assert self.home_page.is_hero_banner_visible() is True, "首頁大看板未能正常顯示"
        
        # 2. 執行切換 (測試按鈕功能)
        self.home_page.switch_hero_banner_next()
        
        # 3. 驗證點擊跳轉
        initial_windows = self.home_page.driver.window_handles
        
        # 執行點擊 (內部已包含針對 Active Banner 的動態等待)
        self.home_page.click_hero_banner()
        
        # 4. 嚴格動態等待：直到新分頁數量變多，最長等待 10 秒
        self.home_page.wait.until(
            lambda d: len(d.window_handles) > len(initial_windows),
            message="點擊大看板後，視窗數量未增加"
        )
        
        # 最終斷言
        assert len(self.home_page.driver.window_handles) > len(initial_windows), "未能開啟新分頁"