"""mobile_pack conftest: Selenium mobile-emulation driver fixture + Allure screenshot hook."""
from __future__ import annotations

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.settings import settings


def _build_mobile_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    opts.add_experimental_option("mobileEmulation", {"deviceName": "iPhone X"})
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    return webdriver.Chrome(options=opts)


@pytest.fixture
def mobile_driver():
    """Function-scoped Selenium iPhone-emulation driver — isolated per test."""
    driver = _build_mobile_driver(headless=settings.headless)
    yield driver
    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshot to Allure whenever a mobile UI test fails or is skipped."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call" or not (rep.failed or rep.skipped):
        return
    drv = item.funcargs.get("mobile_driver")
    if drv is None:
        return
    try:
        allure.attach(
            drv.get_screenshot_as_png(),
            name=f"screenshot-{item.name}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass
