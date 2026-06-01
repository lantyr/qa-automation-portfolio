"""
Suite: SauceDemo mobile login (Selenium iPhone X emulation)
Covers happy path, locked-out user, and credential validation.
"""
import allure
import pytest

from config.settings import settings
from mobile_pack.pages.inventory_page import InventoryPage
from mobile_pack.pages.login_page import LoginPage


@allure.feature("Login")
@pytest.mark.ui
@pytest.mark.mobile
@pytest.mark.smoke
class TestMobileLogin:
    """
    M-LOG-001: Standard user logs in and lands on inventory page.
    Steps:
      1. Visit /
      2. Submit standard_user / secret_sauce
      3. Verify Products header visible
    Expected: redirected to /inventory.html with Products header.
    """

    def test_standard_user_login(self, mobile_driver):
        login = LoginPage(mobile_driver)
        login.visit(settings.sauce_base_url)
        login.login(settings.sauce_user_standard, settings.sauce_password)
        assert InventoryPage(mobile_driver).is_loaded()

    """
    M-LOG-002: Locked-out user sees friendly error, not a server crash.
    Steps:
      1. Submit locked_out_user / secret_sauce
    Expected: error banner contains "locked out".
    """

    @pytest.mark.negative
    def test_locked_out_user_shows_error(self, mobile_driver):
        login = LoginPage(mobile_driver)
        login.visit(settings.sauce_base_url)
        login.login(settings.sauce_user_locked, settings.sauce_password)
        assert login.has_error()
        assert "locked out" in login.error_text().lower()

    """
    M-LOG-003: Wrong password is rejected without leaking account existence.
    Steps:
      1. Submit standard_user / wrong-password
    Expected: generic error visible; no indication of whether account exists.
    """

    @pytest.mark.negative
    def test_invalid_password_rejected(self, mobile_driver):
        login = LoginPage(mobile_driver)
        login.visit(settings.sauce_base_url)
        login.login(settings.sauce_user_standard, "wrong-password")
        assert login.has_error()
        assert "username and password do not match" in login.error_text().lower()
