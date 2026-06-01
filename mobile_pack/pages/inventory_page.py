from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class InventoryPage(BasePage):
    url_path = "/inventory.html"

    def is_loaded(self) -> bool:
        return self._visible(By.CSS_SELECTOR, ".title").text == "Products"

    def item_count(self) -> int:
        return len(self._present_all(By.CSS_SELECTOR, ".inventory_item"))

    def item_names(self) -> list[str]:
        return [el.text for el in self._present_all(By.CSS_SELECTOR, ".inventory_item_name")]

    def item_prices(self) -> list[float]:
        return [
            float(el.text.replace("$", ""))
            for el in self._present_all(By.CSS_SELECTOR, ".inventory_item_price")
        ]

    def sort_by(self, value: str) -> None:
        dropdown = self._visible(By.CSS_SELECTOR, '[data-test="product-sort-container"]')
        Select(dropdown).select_by_value(value)

    def add_first_item_to_cart(self) -> str:
        items = self._present_all(By.CSS_SELECTOR, ".inventory_item")
        name = items[0].find_element(By.CSS_SELECTOR, ".inventory_item_name").text
        items[0].find_element(By.TAG_NAME, "button").click()
        return name

    def cart_count(self) -> int:
        if not self._is_visible(By.CSS_SELECTOR, ".shopping_cart_badge"):
            return 0
        return int(self._visible(By.CSS_SELECTOR, ".shopping_cart_badge").text)

    def open_cart(self) -> None:
        self._clickable(By.CSS_SELECTOR, ".shopping_cart_link").click()

    def open_menu(self) -> None:
        self._clickable(By.ID, "react-burger-menu-btn").click()

    def menu_is_open(self) -> bool:
        try:
            el = self._wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".bm-menu-wrap"))
            )
            return el.get_attribute("aria-hidden") == "false"
        except Exception:
            return False

    def close_menu(self) -> None:
        self._wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, ".bm-menu-wrap").get_attribute("aria-hidden") == "false"
        )
        self._clickable(By.ID, "react-burger-cross-btn").click()

    def nav_items(self) -> list[str]:
        return [
            el.text
            for el in self._present_all(By.CSS_SELECTOR, ".bm-item-list .bm-item")
            if el.text.strip()
        ]
