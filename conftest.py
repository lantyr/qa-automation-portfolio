import os

import pytest

import config.credentials  # noqa: F401 - 載入 .env
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def _build_chrome_options():
    opts = Options()
    if os.getenv("PYTEST_HEADLESS", "1").lower() in ("1", "true", "yes"):
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    return opts


@pytest.fixture
def driver():
    drv = webdriver.Chrome(options=_build_chrome_options())
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


@pytest.fixture(scope="class")
def class_driver():
    """整個測試類別共享同一個瀏覽器 session，適用於需要保持登入狀態的連續測試"""
    drv = webdriver.Chrome(options=_build_chrome_options())
    drv.implicitly_wait(10)
    yield drv
    drv.quit()
