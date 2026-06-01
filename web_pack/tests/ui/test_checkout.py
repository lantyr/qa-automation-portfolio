"""
Suite: SauceDemo PC checkout flow (Playwright Chromium)
End-to-end purchase from product list through confirmation.
"""
import json
from pathlib import Path

import allure
import pytest

from config.settings import settings
from web_pack.pages.checkout_page import CartPage, CheckoutCompletePage, CheckoutPage
from web_pack.pages.inventory_page import InventoryPage
from web_pack.pages.login_page import LoginPage

CHECKOUT_INFO = json.loads(
    (Path(__file__).resolve().parents[3] / "data" / "users.json").read_text()
)["checkout_info"]


@allure.feature("Checkout")
@pytest.mark.ui
@pytest.mark.web
@pytest.mark.smoke
class TestWebCheckout:
    """
    UI-CHK-001: Add to cart updates cart badge count.
    Steps:
      1. Log in
      2. Add first item to cart
    Expected: cart badge shows 1.
    """

    def test_add_to_cart_updates_badge(self, driver):
        LoginPage(driver).visit(settings.sauce_base_url)
        LoginPage(driver).login(settings.sauce_user_standard, settings.sauce_password)
        inv = InventoryPage(driver)
        inv.add_first_item_to_cart()
        assert inv.cart_count() == 1

    """
    UI-CHK-002: End-to-end checkout completes with confirmation.
    Steps:
      1. Log in, add an item, open cart, checkout, fill info, finish
    Expected: confirmation header "Thank you for your order!".
    """

    def test_full_checkout_flow(self, driver):
        LoginPage(driver).visit(settings.sauce_base_url)
        LoginPage(driver).login(settings.sauce_user_standard, settings.sauce_password)

        inv = InventoryPage(driver)
        added_item = inv.add_first_item_to_cart()
        inv.open_cart()

        cart = CartPage(driver)
        assert added_item in cart.item_names()
        cart.checkout()

        CheckoutPage(driver).fill_info(**CHECKOUT_INFO)
        CheckoutPage(driver).finish()

        confirmation = CheckoutCompletePage(driver).confirmation_text()
        assert "thank you" in confirmation.lower()
