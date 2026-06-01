from playwright.sync_api import Browser, Page, Playwright, sync_playwright


def build_chrome(headless: bool = True) -> tuple[Playwright, Browser, Page]:
    """Launch a Chromium browser via Playwright and return a ready Page.

    Run ``playwright install chromium`` once after installing dependencies.
    Returns (playwright, browser, page) so the caller can close them properly.
    """
    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=headless,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
    )
    page = browser.new_context(
        viewport={"width": 1280, "height": 800}
    ).new_page()
    return p, browser, page
