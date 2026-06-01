import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass(frozen=True)
class Settings:
    sauce_base_url: str = os.getenv("SAUCE_BASE_URL", "https://www.saucedemo.com")
    reqres_base_url: str = os.getenv("REQRES_BASE_URL", "https://reqres.in/api")

    sauce_user_standard: str = os.getenv("SAUCE_USER_STANDARD", "standard_user")
    sauce_user_locked: str = os.getenv("SAUCE_USER_LOCKED", "locked_out_user")
    sauce_user_problem: str = os.getenv("SAUCE_USER_PROBLEM", "problem_user")
    sauce_password: str = os.getenv("SAUCE_PASSWORD", "secret_sauce")

    reqres_api_key: str = os.getenv("REQRES_API_KEY", "reqres-free-v1")

    browser_mode: str = os.getenv("BROWSER_MODE", "headless")

    @property
    def headless(self) -> bool:
        return self.browser_mode.lower() == "headless"


settings = Settings()
