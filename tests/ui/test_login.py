"""
Suite: SauceDemo login
Covers happy path, locked-out user, and credential validation.
"""
import allure
import pytest

from src.config import settings
from src.pages import InventoryPage, LoginPage


@allure.feature("Login")
@pytest.mark.ui
@pytest.mark.smoke
class TestLogin:
    """
    UI-LOG-001: Standard user logs in and lands on inventory page.
    Steps:
      1. Visit /
      2. Submit standard_user / secret_sauce
      3. Verify Products header visible
    Expected: redirected to /inventory.html with Products header.
    """

    def test_standard_user_login(self, driver):
        login = LoginPage(driver)
        login.visit(settings.sauce_base_url)
        login.login(settings.sauce_user_standard, settings.sauce_password)
        assert InventoryPage(driver).is_loaded()

    """
    UI-LOG-002: Locked-out user sees friendly error, not a server crash.
    Steps:
      1. Submit locked_out_user / secret_sauce
    Expected: error banner with "locked out" message.
    """

    @pytest.mark.negative
    def test_locked_out_user_shows_error(self, driver):
        login = LoginPage(driver)
        login.visit(settings.sauce_base_url)
        login.login(settings.sauce_user_locked, settings.sauce_password)
        assert login.has_error()
        assert "locked out" in login.error_text().lower()

    """
    UI-LOG-003: Wrong password is rejected with credential error (no information leak).
    Steps:
      1. Submit standard_user / wrong-password
    Expected: error visible; message does not differentiate user-exists vs wrong-pass.
    """

    @pytest.mark.negative
    def test_invalid_password_rejected(self, driver):
        login = LoginPage(driver)
        login.visit(settings.sauce_base_url)
        login.login(settings.sauce_user_standard, "wrong-password")
        assert login.has_error()
        msg = login.error_text().lower()
        assert "username and password do not match" in msg
