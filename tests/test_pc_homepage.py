"""
PC 版官網：首頁功能驗證。

Test ID 範圍：TC-PC-HP-001 ~ TC-PC-HP-008
  001 → 首頁開啟正常
  002 → 大看板顯示正常
  003 → 大看板連結正常
  004 → 大看板切換正常
  005 → 最新消息顯示正常
  006 → 最新消息連結正常
  007 → Chatbot 浮水印顯示正常
  008 → Chatbot 浮水印連結正常

整個類別共享同一個 class_driver，以減少頁面請求降低 429 風險。
"""
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config.credentials  # noqa: F401 - 載入 .env
from pages.home_page import HomePage


def _screenshot(driver, name: str) -> None:
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


@allure.feature("PC版官網首頁功能驗證")
class TestPCHomePage:

    @pytest.fixture(autouse=True)
    def _setup(self, class_driver):
        self.driver = class_driver
        try:
            class_driver.switch_to.default_content()
        except Exception:
            pass
        HomePage(class_driver).go_to_home_if_needed()

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-001：開啟遊戲橘子首頁顯示正常")
    def test_tc_pc_hp_001_home_open(self):
        # Test ID: TC-PC-HP-001
        # Test Title: 開啟遊戲橘子首頁顯示正常
        # Test Steps:
        #   1. 前往首頁 URL
        #   2. 驗證 LOGO 可見，頁面正常載入
        # Expected Result: LOGO 元素於超時內可見

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁載入")

        with allure.step("2. 驗證 LOGO 可見"):
            home.wait_until_visible(HomePage.LOGO)
            _screenshot(self.driver, "步驟2_LOGO可見")

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-002：大看板顯示正常")
    def test_tc_pc_hp_002_banner_display(self):
        # Test ID: TC-PC-HP-002
        # Test Title: 大看板顯示正常
        # Test Steps:
        #   1. 前往首頁
        #   2. 驗證大看板 iframe 可見
        #   3. 切換至 iframe，驗證輪播容器存在
        # Expected Result: iframe 可見且輪播容器存在

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 驗證大看板 iframe 可見"):
            home.wait_until_visible(HomePage.BANNER_IFRAME)
            _screenshot(self.driver, "步驟2_banner_iframe可見")

        with allure.step("3. 切換至 iframe 驗證輪播容器"):
            iframe = self.driver.find_element(*HomePage.BANNER_IFRAME)
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(HomePage.BANNER_CONTAINER)
            )
            _screenshot(self.driver, "步驟3_輪播容器存在")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-003：大看板連結正常")
    def test_tc_pc_hp_003_banner_link(self):
        # Test ID: TC-PC-HP-003
        # Test Title: 大看板連結正常
        # Test Steps:
        #   1. 前往首頁
        #   2. 切換至大看板 iframe
        #   3. 驗證輪播中有 href 的連結存在
        # Expected Result: 至少一個 banner 連結具有有效 href

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2-3. 切換至 iframe 驗證 banner 連結"):
            iframe = self.driver.find_element(*HomePage.BANNER_IFRAME)
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(HomePage.BANNER_CONTAINER)
            )
            links = self.driver.find_elements(By.CSS_SELECTOR, "ul.bxslider li a[href]")
            assert len(links) > 0, "大看板內找不到任何含 href 的連結"
            href = links[0].get_attribute("href")
            assert href and href.strip(), "大看板第一個連結的 href 為空"
            _screenshot(self.driver, "步驟2_3_banner連結驗證")
            self.driver.switch_to.default_content()

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-004：大看板切換正常")
    def test_tc_pc_hp_004_banner_switch(self):
        # Test ID: TC-PC-HP-004
        # Test Title: 大看板切換正常
        # Test Steps:
        #   1. 前往首頁
        #   2. 驗證右側切換按鈕可見
        #   3. 點擊右側切換按鈕
        #   4. 驗證左側切換按鈕可見並可點擊
        # Expected Result: 切換按鈕可正常點擊

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 驗證右側切換按鈕可見"):
            home.wait_until_visible(HomePage.BANNER_NEXT_BTN)
            _screenshot(self.driver, "步驟2_右鍵可見")

        with allure.step("3. 點擊右側切換按鈕"):
            home.click_element_safely(HomePage.BANNER_NEXT_BTN)
            _screenshot(self.driver, "步驟3_點擊右鍵後")

        with allure.step("4. 驗證左側切換按鈕可見"):
            home.wait_until_visible(HomePage.BANNER_PREV_BTN)
            _screenshot(self.driver, "步驟4_左鍵可見")

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-005
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-005：最新消息顯示正常")
    def test_tc_pc_hp_005_news_display(self):
        # Test ID: TC-PC-HP-005
        # Test Title: 最新消息顯示正常
        # Test Steps:
        #   1. 前往首頁
        #   2. 驗證最新消息容器可見
        #   3. 驗證至少有一筆消息列表項目
        # Expected Result: 最新消息區塊可見且有消息項目

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 驗證最新消息容器可見"):
            home.wait_until_visible(HomePage.NEWS_CONTAINER)
            _screenshot(self.driver, "步驟2_消息容器可見")

        with allure.step("3. 驗證至少有一筆消息項目"):
            items = self.driver.find_elements(*HomePage.NEWS_LIST_ITEMS)
            assert len(items) > 0, "最新消息列表為空"
            _screenshot(self.driver, "步驟3_消息項目存在")

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-006
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-006：最新消息連結正常")
    def test_tc_pc_hp_006_news_link(self):
        # Test ID: TC-PC-HP-006
        # Test Title: 最新消息連結正常
        # Test Steps:
        #   1. 前往首頁
        #   2. 驗證第一筆消息連結可見且有效 href
        #   3. 點擊連結（開新分頁）
        #   4. 驗證新分頁已開啟且 URL 包含 news
        # Expected Result: 點擊後新分頁開啟，URL 含 news 路徑

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 驗證第一筆消息連結有效"):
            link_el = home.wait_until_visible(HomePage.NEWS_FIRST_ITEM_LINK)
            href = link_el.get_attribute("href")
            assert href and "news" in href, f"連結 href 無效：{href}"
            _screenshot(self.driver, "步驟2_連結有效")

        with allure.step("3. 點擊連結"):
            original_handles = self.driver.window_handles
            link_el.click()
            _screenshot(self.driver, "步驟3_點擊後")

        with allure.step("4. 驗證新分頁開啟"):
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.window_handles) > len(original_handles)
            )
            self.driver.switch_to.window(self.driver.window_handles[-1])
            WebDriverWait(self.driver, 10).until(EC.url_contains("news"))
            _screenshot(self.driver, "步驟4_新分頁URL驗證")
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-007
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-007：右下角 Chatbot 浮水印顯示正常")
    def test_tc_pc_hp_007_chatbot_display(self):
        # Test ID: TC-PC-HP-007
        # Test Title: 右下角 Chatbot 浮水印顯示正常
        # Test Steps:
        #   1. 前往首頁
        #   2. 驗證 Chatbot 按鈕可見
        # Expected Result: id="gim-bot-tool-button" 可見

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 驗證 Chatbot 按鈕可見"):
            home.wait_until_visible(HomePage.CHATBOT_BTN)
            _screenshot(self.driver, "步驟2_chatbot可見")

    # ────────────────────────────────────────────────────────────
    # TC-PC-HP-008
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-PC-HP-008：右下角 Chatbot 浮水印連結正常")
    def test_tc_pc_hp_008_chatbot_link(self):
        # Test ID: TC-PC-HP-008
        # Test Title: 右下角 Chatbot 浮水印連結正常
        # Test Steps:
        #   1. 前往首頁
        #   2. 點擊 Chatbot 按鈕
        #   3. 驗證客服視窗標題出現
        # Expected Result: 點擊後客服視窗「遊戲橘子客服小幫手」標題可見

        home = HomePage(self.driver)

        with allure.step("1. 前往首頁"):
            home.go_to_home_if_needed()
            _screenshot(self.driver, "步驟1_首頁")

        with allure.step("2. 點擊 Chatbot 按鈕"):
            home.click_chatbot()
            _screenshot(self.driver, "步驟2_點擊chatbot後")

        with allure.step("3. 驗證客服視窗標題出現"):
            home.wait_until_visible(HomePage.CHATBOT_WINDOW_TITLE)
            _screenshot(self.driver, "步驟3_客服視窗標題可見")
