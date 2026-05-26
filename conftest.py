"""Root conftest: shared fixtures and Allure hooks for API + UI tests."""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Error as PlaywrightError

from src.api import ReqResClient
from src.config import settings
from src.utils.driver_factory import build_chrome


@pytest.fixture(scope="session")
def reqres() -> ReqResClient:
    """Session-scoped API client. Stateless, safe to share."""
    return ReqResClient()


@pytest.fixture
def driver():
    """Function-scoped Playwright page — fresh browser per test for isolation."""
    p, browser, page = build_chrome(headless=settings.headless)
    yield page
    browser.close()
    p.stop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Promote Playwright errors to AssertionError so Allure marks them
    Failed (red) instead of Broken (yellow).
    """
    outcome = yield
    excinfo = outcome.excinfo
    if excinfo is not None:
        _, exc_value, _ = excinfo
        if isinstance(exc_value, PlaywrightError):
            raise AssertionError(str(exc_value)) from exc_value


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to Allure whenever a UI test fails or is skipped."""
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
