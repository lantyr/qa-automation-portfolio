import pytest
from pages.home_page import HomePage

class TestHomepageVideo:
    """
    Test ID: TC_HOME_VID_001
    Test Title: 首頁 YouTube 合作影片播放測試
    Test Steps:
        1. 導航至 Beanfun 首頁 (https://tw.beanfun.com/)
        2. 捲動至 YouTube 影片 iframe 區塊
        3. 切換至 iframe 內部並點擊中央大型播放鍵
        4. 驗證影片是否正常播放 (判斷播放鍵是否消失)
    Expected Result:
        點擊播放按鈕後，影片應能正常執行（大播放鍵消失）。若點擊無效或無播放反應，拋出明確的 AssertionError。
    """

    def test_youtube_video_playback(self, driver):
        # 1. 初始化 Page Object
        home_page = HomePage(driver)

        # 2. 前往首頁並等待載入完成
        home_page.go_to_home()

        # 3. 執行播放操作
        # 這裡會自動處理捲動與 iframe 的切入/切出
        home_page.play_youtube_video()

        # 4. 驗證是否能執行 (如果沒有執行，POM 內層會直接 raise AssertionError 報錯)
        is_playing = home_page.verify_youtube_is_playing()
        assert is_playing is True, "YouTube 影片未能成功切換至播放狀態"