"""
PC 版官網：會員中心自動化測試。

涵蓋範圍：
  - 點帳進入會員中心
  - 星帳進入會員中心
"""
import allure
import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage


@allure.feature("PC版官網會員中心")
class TestPCMemberCenter:

    @pytest.fixture(autouse=True)
    def _setup(self, driver):
        self.driver = driver
        self.home = HomePage(self.driver)
        self.login = LoginPage(self.driver)

    # TC 待補
