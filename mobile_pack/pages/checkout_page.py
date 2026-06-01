from selenium.webdriver.common.by import By

from .base_page import BasePage


class CartPage(BasePage):
    url_path = "/cart.html"

    def is_loaded(self) -> bool:
        return self._visible(By.CSS_SELECTOR, ".title").text == "Your Cart"

    def item_names(self) -> list[str]:
        return [el.text for el in self._present_all(By.CSS_SELECTOR, ".inventory_item_name")]

    def checkout(self) -> None:
        self._clickable(By.ID, "checkout").click()


class CheckoutPage(BasePage):
    url_path = "/checkout-step-one.html"

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        self._visible(By.ID, "first-name").send_keys(first_name)
        self._visible(By.ID, "last-name").send_keys(last_name)
        self._visible(By.ID, "postal-code").send_keys(postal_code)
        self._clickable(By.ID, "continue").click()

    def finish(self) -> None:
        self._clickable(By.ID, "finish").click()


class CheckoutCompletePage(BasePage):
    url_path = "/checkout-complete.html"

    def confirmation_text(self) -> str:
        return self._visible(By.CSS_SELECTOR, ".complete-header").text
