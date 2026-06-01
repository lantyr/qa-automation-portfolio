"""web_pack conftest: Playwright fixture + Allure screenshot hook."""
from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from config.settings import settings
from src.api import ReqResClient


def _build_page(headless: bool = True):
    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=headless,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
    )
    page = browser.new_context(viewport={"width": 1280, "height": 800}).new_page()
    return p, browser, page


@pytest.fixture
def driver():
    """Function-scoped Playwright page — fresh browser per test for isolation."""
    p, browser, page = _build_page(headless=settings.headless)
    yield page
    browser.close()
    p.stop()


@pytest.fixture(scope="session")
def reqres() -> ReqResClient:
    """Session-scoped reqres.in API client."""
    return ReqResClient()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Convert Playwright errors to AssertionError so Allure marks them Failed (red)."""
    outcome = yield
    excinfo = outcome.excinfo
    if excinfo is not None:
        _, exc_value, _ = excinfo
        if isinstance(exc_value, PlaywrightError):
            raise AssertionError(str(exc_value)) from exc_value


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshot to Allure whenever a PC UI test fails or is skipped."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call" or not (rep.failed or rep.skipped):
        return
    drv = item.funcargs.get("driver")
    if drv is None:
        return
    try:
        allure.attach(
            drv.screenshot(),
            name=f"screenshot-{item.name}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass
