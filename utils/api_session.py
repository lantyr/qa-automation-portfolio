"""
Build a requests Session pre-loaded with cookies extracted from a Playwright page.

Useful for API assertions that need to share session state with a UI test —
e.g., verifying that a server-side side-effect triggered by the UI is
visible via a direct API call.
"""
from __future__ import annotations

import requests
from playwright.sync_api import Page


def session_from_page(page: Page) -> requests.Session:
    """Return a requests Session carrying all cookies from the given Playwright page."""
    session = requests.Session()
    for cookie in page.context.cookies():
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
        )
    session.headers.update({"Accept": "application/json"})
    return session
