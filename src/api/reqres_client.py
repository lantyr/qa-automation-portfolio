from typing import Any

import requests

from src.config import settings


class ReqResClient:
    """Thin wrapper over reqres.in for tests.

    Centralises base URL, headers, and timeouts so individual tests stay
    declarative.
    """

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or settings.reqres_base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-api-key": settings.reqres_api_key,
                "Accept": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def list_users(self, page: int = 1) -> requests.Response:
        return self.session.get(self._url("/users"), params={"page": page}, timeout=self.timeout)

    def get_user(self, user_id: int) -> requests.Response:
        return self.session.get(self._url(f"/users/{user_id}"), timeout=self.timeout)

    def create_user(self, payload: dict[str, Any]) -> requests.Response:
        return self.session.post(self._url("/users"), json=payload, timeout=self.timeout)

    def update_user(self, user_id: int, payload: dict[str, Any]) -> requests.Response:
        return self.session.put(self._url(f"/users/{user_id}"), json=payload, timeout=self.timeout)

    def delete_user(self, user_id: int) -> requests.Response:
        return self.session.delete(self._url(f"/users/{user_id}"), timeout=self.timeout)

    def register(self, email: str, password: str) -> requests.Response:
        return self.session.post(
            self._url("/register"),
            json={"email": email, "password": password},
            timeout=self.timeout,
        )

    def login(self, email: str, password: str) -> requests.Response:
        return self.session.post(
            self._url("/login"),
            json={"email": email, "password": password},
            timeout=self.timeout,
        )
