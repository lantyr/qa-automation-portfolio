"""
Suite: SauceDemo PC inventory (Playwright Chromium)
Covers product listing and sort behaviour on desktop viewport.
"""
import allure
import pytest

from config.settings import settings
from web_pack.pages.inventory_page import InventoryPage
from web_pack.pages.login_page import LoginPage


@pytest.fixture
def logged_in_inventory(driver):
    LoginPage(driver).visit(settings.sauce_base_url)
    LoginPage(driver).login(settings.sauce_user_standard, settings.sauce_password)
    inv = InventoryPage(driver)
    assert inv.is_loaded()
    return inv


@allure.feature("Inventory")
@pytest.mark.ui
@pytest.mark.web
class TestWebInventory:
    """
    UI-INV-001: Inventory page lists exactly 6 products for standard user.
    Steps:
      1. Log in
      2. Count items on inventory page
    Expected: 6 items.
    """

    def test_inventory_shows_six_products(self, logged_in_inventory):
        assert logged_in_inventory.item_count() == 6

    """
    UI-INV-002: Sort by price low-to-high orders prices ascending.
    Steps:
      1. Select sort = "lohi"
      2. Read all prices
    Expected: prices are non-decreasing.
    """

    def test_sort_price_low_to_high(self, logged_in_inventory):
        logged_in_inventory.sort_by("lohi")
        prices = logged_in_inventory.item_prices()
        assert prices == sorted(prices), f"Prices not ascending: {prices}"

    """
    UI-INV-003: Sort by name Z-to-A orders names descending.
    Steps:
      1. Select sort = "za"
      2. Read all names
    Expected: names are reverse-alphabetical.
    """

    def test_sort_name_z_to_a(self, logged_in_inventory):
        logged_in_inventory.sort_by("za")
        names = logged_in_inventory.item_names()
        assert names == sorted(names, reverse=True), f"Names not Z->A: {names}"
