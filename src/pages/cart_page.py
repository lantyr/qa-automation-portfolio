from .base_page import BasePage


class CartPage(BasePage):
    url_path = "/cart.html"

    TITLE = ".title"
    ITEM = ".cart_item"
    ITEM_NAME = ".inventory_item_name"
    CHECKOUT_BUTTON = "#checkout"
    CONTINUE_SHOPPING = "#continue-shopping"

    def is_loaded(self) -> bool:
        return self._visible(self.TITLE).inner_text() == "Your Cart"

    def item_names(self) -> list[str]:
        return [el.inner_text() for el in self._present_all(self.ITEM_NAME)]

    def checkout(self) -> None:
        self._clickable(self.CHECKOUT_BUTTON).click()
