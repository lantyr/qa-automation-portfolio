"""
Suite: ReqRes /register and /login
Covers happy-path auth plus negative cases the spec documents.
"""
import json
from pathlib import Path

import allure
import pytest

USERS = json.loads((Path(__file__).resolve().parents[2] / "data" / "users.json").read_text())


@allure.feature("Auth API")
@pytest.mark.api
@pytest.mark.smoke
class TestRegister:
    """
    AUT-001: Successful registration returns id + token.
    Steps:
      1. POST /register with documented valid credentials
      2. Assert 200 + id + token
    Expected: 200 with non-empty id and token.
    """

    def test_register_success(self, reqres):
        creds = USERS["valid_register"]
        response = reqres.register(creds["email"], creds["password"])
        assert response.status_code == 200
        body = response.json()
        assert body["id"]
        assert body["token"]

    """
    AUT-002 (negative): Registration without password returns 400.
    Steps:
      1. POST /register with missing password
    Expected: 400 + "Missing password" error message.
    """

    @pytest.mark.negative
    def test_register_missing_password(self, reqres):
        creds = USERS["missing_password"]
        response = reqres.register(creds["email"], "")
        assert response.status_code == 400
        assert "password" in response.json()["error"].lower()


@allure.feature("Auth API")
@pytest.mark.api
class TestLogin:
    """
    AUT-003: Successful login returns token.
    Steps:
      1. POST /login with documented valid credentials
      2. Assert 200 + token
    Expected: 200 with non-empty token.
    """

    def test_login_success(self, reqres):
        creds = USERS["valid_login"]
        response = reqres.login(creds["email"], creds["password"])
        assert response.status_code == 200
        assert response.json()["token"]

    """
    AUT-004 (negative): Login with unknown user returns 400.
    Steps:
      1. POST /login with email not in dataset
    Expected: 400 + "user not found" error.
    """

    @pytest.mark.negative
    def test_login_unknown_user(self, reqres):
        response = reqres.login("ghost@nowhere.com", "anything")
        assert response.status_code == 400
        assert "user" in response.json()["error"].lower()
