from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    url_path = "/"

    def login(self, username: str, password: str) -> None:
        self._visible(By.ID, "user-name").send_keys(username)
        self._visible(By.ID, "password").send_keys(password)
        self._clickable(By.ID, "login-button").click()

    def error_text(self) -> str:
        return self._visible(By.CSS_SELECTOR, '[data-test="error"]').text

    def has_error(self) -> bool:
        return self._is_visible(By.CSS_SELECTOR, '[data-test="error"]')
