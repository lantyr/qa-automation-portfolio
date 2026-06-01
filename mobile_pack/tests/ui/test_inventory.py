"""
Suite: SauceDemo mobile inventory (Selenium iPhone X emulation)
Covers product listing and sort behaviour on mobile viewport.
"""
import allure
import pytest

from config.settings import settings
from mobile_pack.pages.inventory_page import InventoryPage
from mobile_pack.pages.login_page import LoginPage


@pytest.fixture
def logged_in_inventory(mobile_driver):
    login = LoginPage(mobile_driver)
    login.visit(settings.sauce_base_url)
    login.login(settings.sauce_user_standard, settings.sauce_password)
    inv = InventoryPage(mobile_driver)
    assert inv.is_loaded()
    return inv


@allure.feature("Inventory")
@pytest.mark.ui
@pytest.mark.mobile
class TestMobileInventory:
    """
    M-INV-001: Mobile inventory page lists exactly 6 products.
    Steps:
      1. Log in on mobile
      2. Count items on inventory page
    Expected: 6 items visible.
    """

    def test_inventory_shows_six_products(self, logged_in_inventory):
        assert logged_in_inventory.item_count() == 6

    """
    M-INV-002: Sort by price low-to-high orders prices ascending.
    Steps:
      1. Select sort option "lohi"
      2. Read all item prices
    Expected: prices are non-decreasing.
    """

    def test_sort_price_low_to_high(self, logged_in_inventory):
        logged_in_inventory.sort_by("lohi")
        prices = logged_in_inventory.item_prices()
        assert prices == sorted(prices), f"Prices not ascending: {prices}"
