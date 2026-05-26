from .base_page import BasePage


class CheckoutPage(BasePage):
    url_path = "/checkout-step-one.html"

    FIRST_NAME = "#first-name"
    LAST_NAME = "#last-name"
    POSTAL_CODE = "#postal-code"
    CONTINUE = "#continue"
    FINISH = "#finish"

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        self._visible(self.FIRST_NAME).fill(first_name)
        self._visible(self.LAST_NAME).fill(last_name)
        self._visible(self.POSTAL_CODE).fill(postal_code)
        self._clickable(self.CONTINUE).click()

    def finish(self) -> None:
        self._clickable(self.FINISH).click()


class CheckoutCompletePage(BasePage):
    url_path = "/checkout-complete.html"

    HEADER = ".complete-header"

    def confirmation_text(self) -> str:
        return self._visible(self.HEADER).inner_text()
