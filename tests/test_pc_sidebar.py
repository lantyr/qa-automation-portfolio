"""
PC 版官網：側欄自動化測試。

涵蓋範圍（待補）：

  點帳：
    - 側欄帳號顯示
    - 側欄目前點數顯示
    - 側欄重新整理點數功能
    - 側欄功能顯示（大分類）
    - 點擊側欄大分類（會員資料、服務開通、查詢紀錄、會員須知）
    - 點擊子項目（開通權益、電子報、簡訊、帳號大事紀、遊戲使用紀錄…等）

  星帳：
    - 側欄帳號顯示
    - 側欄目前點數顯示
    - 側欄重新整理點數功能
    - 側欄功能顯示（大分類）
    - 點擊側欄大分類（會員資料、帳號整合、服務開通、查詢紀錄、會員須知）
    - 點擊子項目（同點帳）
"""
import allure
import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage


@allure.feature("PC版官網側欄")
class TestPCSidebarPureAccount:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(driver)
        self.login = LoginPage(driver)

    # TC 待補（點帳側欄）


@allure.feature("PC版官網側欄")
class TestPCSidebarStarAccount:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(driver)
        self.login = LoginPage(driver)

    # TC 待補（星帳側欄）
