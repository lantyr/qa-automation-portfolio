import json
import os
import shutil
from pathlib import Path

import allure
import pytest

import config.credentials  # noqa: F401 - 載入 .env
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_configure(config):
    """將 categories.json 複製至 allure-results，讓 Allure 報告顯示「被鎖定」分類欄位。"""
    allure_dir = Path(config.option.allure_report_dir) if hasattr(config.option, "allure_report_dir") and config.option.allure_report_dir else Path("allure-results")
    allure_dir.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).parent / "categories.json"
    if src.exists():
        shutil.copy2(src, allure_dir / "categories.json")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """test_pc_topup_store 測試失敗時自動截圖並附加至 Allure 報告。"""
    outcome = yield
    rep = outcome.get_result()
    _SCREENSHOT_TESTS = ("test_pc_topup_store", "test_pc_navbar_states")
    if rep.when == "call" and rep.failed and any(t in item.nodeid for t in _SCREENSHOT_TESTS):
        driver = item.funcargs.get("class_driver") or item.funcargs.get("driver")
        if driver:
            try:
                driver.switch_to.alert.dismiss()
            except Exception:
                pass
            try:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="失敗截圖",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass


def _build_chrome_options():
    opts = Options()
    if os.getenv("PYTEST_HEADLESS", "1").lower() in ("1", "true", "yes"):
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    return opts


def _safe_quit(drv):
    """quit 前先 dismiss 殘留 alert，避免 ChromeDriver INTERNALERROR。"""
    try:
        drv.switch_to.alert.dismiss()
    except Exception:
        pass
    drv.quit()


@pytest.fixture
def driver():
    drv = webdriver.Chrome(options=_build_chrome_options())
    drv.implicitly_wait(10)
    yield drv
    _safe_quit(drv)


@pytest.fixture(scope="class")
def class_driver():
    """整個測試類別共享同一個瀏覽器 session，適用於需要保持登入狀態的連續測試"""
    drv = webdriver.Chrome(options=_build_chrome_options())
    drv.implicitly_wait(10)
    yield drv
    _safe_quit(drv)
