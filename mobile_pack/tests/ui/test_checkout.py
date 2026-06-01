"""
Suite: SauceDemo mobile checkout & navigation (Selenium iPhone X emulation)
Covers cart badge, end-to-end purchase flow, and hamburger menu.
"""
import json
from pathlib import Path

import allure
import pytest

from config.settings import settings
from mobile_pack.pages.checkout_page import CartPage, CheckoutCompletePage, CheckoutPage
from mobile_pack.pages.inventory_page import InventoryPage
from mobile_pack.pages.login_page import LoginPage

CHECKOUT_INFO = json.loads(
    (Path(__file__).resolve().parents[3] / "data" / "users.json").read_text()
)["checkout_info"]


@allure.feature("Checkout")
@pytest.mark.ui
@pytest.mark.mobile
@pytest.mark.smoke
class TestMobileCheckout:
    """
    M-CHK-001: Adding an item to cart updates the cart badge count.
    Steps:
      1. Log in on mobile
      2. Add the first item to cart
    Expected: cart badge shows 1.
    """

    def test_add_to_cart_updates_badge(self, mobile_driver):
        LoginPage(mobile_driver).visit(settings.sauce_base_url)
        LoginPage(mobile_driver).login(settings.sauce_user_standard, settings.sauce_password)
        inv = InventoryPage(mobile_driver)
        inv.add_first_item_to_cart()
        assert inv.cart_count() == 1

    """
    M-CHK-002: End-to-end checkout completes with confirmation message.
    Steps:
      1. Log in, add item, open cart, proceed to checkout, fill info, finish
    Expected: "Thank you for your order!" confirmation header.
    """

    def test_full_checkout_flow(self, mobile_driver):
        LoginPage(mobile_driver).visit(settings.sauce_base_url)
        LoginPage(mobile_driver).login(settings.sauce_user_standard, settings.sauce_password)

        inv = InventoryPage(mobile_driver)
        added_item = inv.add_first_item_to_cart()
        inv.open_cart()

        cart = CartPage(mobile_driver)
        assert added_item in cart.item_names()
        cart.checkout()

        CheckoutPage(mobile_driver).fill_info(**CHECKOUT_INFO)
        CheckoutPage(mobile_driver).finish()

        confirmation = CheckoutCompletePage(mobile_driver).confirmation_text()
        assert "thank you" in confirmation.lower()


@allure.feature("Navigation")
@pytest.mark.ui
@pytest.mark.mobile
class TestMobileNavigation:
    """
    M-NAV-001: Hamburger menu opens, shows expected nav items, and closes.
    Steps:
      1. Log in on mobile
      2. Tap hamburger menu button
      3. Verify menu is open and contains "All Items" and "Logout"
      4. Close the menu
    Expected: menu opens cleanly, contains required items, closes without error.
    """

    def test_hamburger_menu_open_close(self, mobile_driver):
        LoginPage(mobile_driver).visit(settings.sauce_base_url)
        LoginPage(mobile_driver).login(settings.sauce_user_standard, settings.sauce_password)
        inv = InventoryPage(mobile_driver)
        assert inv.is_loaded()

        inv.open_menu()
        assert inv.menu_is_open()

        nav_texts = [t.lower() for t in inv.nav_items()]
        assert any("all items" in t for t in nav_texts)
        assert any("logout" in t for t in nav_texts)

        inv.close_menu()
