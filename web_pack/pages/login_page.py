from .base_page import BasePage


class LoginPage(BasePage):
    url_path = "/"

    USERNAME = "#user-name"
    PASSWORD = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = '[data-test="error"]'

    def login(self, username: str, password: str) -> None:
        self._visible(self.USERNAME).fill(username)
        self._visible(self.PASSWORD).fill(password)
        self._clickable(self.LOGIN_BUTTON).click()

    def error_text(self) -> str:
        return self._visible(self.ERROR_MESSAGE).inner_text()

    def has_error(self) -> bool:
        return self._is_visible(self.ERROR_MESSAGE)
