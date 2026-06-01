from __future__ import annotations

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

DEFAULT_TIMEOUT = 10_000  # milliseconds


class BasePage:
    """Shared waits and primitives for all pages.

    Only dynamic waits — never sleep(). Page subclasses expose
    intent-revealing methods, never raw locators.
    """

    url_path: str = ""

    def __init__(self, page: Page, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.page = page
        self.timeout = timeout

    def visit(self, base_url: str) -> None:
        self.page.goto(f"{base_url.rstrip('/')}/{self.url_path.lstrip('/')}")

    def _visible(self, selector: str) -> Locator:
        loc = self.page.locator(selector)
        loc.wait_for(state="visible", timeout=self.timeout)
        return loc

    def _clickable(self, selector: str) -> Locator:
        loc = self.page.locator(selector)
        loc.wait_for(state="visible", timeout=self.timeout)
        return loc

    def _present_all(self, selector: str) -> list[Locator]:
        loc = self.page.locator(selector)
        loc.first.wait_for(state="attached", timeout=self.timeout)
        return loc.all()

    def _is_visible(self, selector: str) -> bool:
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False
