from .base_page import BasePage


class InventoryPage(BasePage):
    url_path = "/inventory.html"

    TITLE = ".title"
    ITEM = ".inventory_item"
    ITEM_NAME = ".inventory_item_name"
    ITEM_PRICE = ".inventory_item_price"
    SORT_DROPDOWN = '[data-test="product-sort-container"]'
    CART_BADGE = ".shopping_cart_badge"
    CART_LINK = ".shopping_cart_link"

    def is_loaded(self) -> bool:
        return self._visible(self.TITLE).inner_text() == "Products"

    def item_count(self) -> int:
        return len(self._present_all(self.ITEM))

    def item_names(self) -> list[str]:
        return [el.inner_text() for el in self._present_all(self.ITEM_NAME)]

    def item_prices(self) -> list[float]:
        return [
            float(el.inner_text().replace("$", ""))
            for el in self._present_all(self.ITEM_PRICE)
        ]

    def sort_by(self, value: str) -> None:
        self.page.locator(self.SORT_DROPDOWN).select_option(value=value)

    def add_first_item_to_cart(self) -> str:
        item = self._present_all(self.ITEM)[0]
        name = item.locator(self.ITEM_NAME).inner_text()
        item.locator("button").click()
        return name

    def cart_count(self) -> int:
        if not self._is_visible(self.CART_BADGE):
            return 0
        return int(self._visible(self.CART_BADGE).inner_text())

    def open_cart(self) -> None:
        self._clickable(self.CART_LINK).click()
