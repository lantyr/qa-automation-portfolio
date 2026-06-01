from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 10


class BasePage:
    """Selenium base page with dynamic waits only — no sleep() allowed."""

    url_path: str = ""

    def __init__(self, driver: WebDriver, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.driver = driver
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    def visit(self, base_url: str) -> None:
        self.driver.get(f"{base_url.rstrip('/')}/{self.url_path.lstrip('/')}")

    def _visible(self, by: str, selector: str) -> WebElement:
        return self._wait.until(EC.visibility_of_element_located((by, selector)))

    def _clickable(self, by: str, selector: str) -> WebElement:
        return self._wait.until(EC.element_to_be_clickable((by, selector)))

    def _present_all(self, by: str, selector: str) -> list[WebElement]:
        self._wait.until(EC.presence_of_element_located((by, selector)))
        return self.driver.find_elements(by, selector)

    def _is_visible(self, by: str, selector: str) -> bool:
        try:
            self._wait.until(EC.visibility_of_element_located((by, selector)))
            return True
        except TimeoutException:
            return False
