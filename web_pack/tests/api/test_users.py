"""
Suite: ReqRes /users
Covers list pagination, single fetch, 404, and schema integrity.
"""
import allure
import pytest
from jsonschema import validate

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "email", "first_name", "last_name", "avatar"],
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "first_name": {"type": "string", "minLength": 1},
        "last_name": {"type": "string", "minLength": 1},
        "avatar": {"type": "string", "pattern": r"^https?://"},
    },
}


@allure.feature("Users API")
@pytest.mark.api
@pytest.mark.smoke
class TestListUsers:
    """
    USR-001: List users returns paginated payload with valid user records.
    Steps:
      1. GET /users?page=2
      2. Assert 200 + correct page metadata
      3. Validate every user against USER_SCHEMA
    Expected: 200, page=2, data is a non-empty array of well-formed users.
    """

    def test_list_users_page_2(self, reqres):
        response = reqres.list_users(page=2)
        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 2
        assert body["data"], "expected at least one user in data"
        for user in body["data"]:
            validate(instance=user, schema=USER_SCHEMA)


@allure.feature("Users API")
@pytest.mark.api
class TestGetUser:
    """
    USR-002: Single user fetch returns the user wrapped in `data`.
    Steps:
      1. GET /users/2
      2. Assert 200 and payload matches USER_SCHEMA
    Expected: 200 + valid user.
    """

    def test_get_existing_user(self, reqres):
        response = reqres.get_user(2)
        assert response.status_code == 200
        validate(instance=response.json()["data"], schema=USER_SCHEMA)

    """
    USR-003 (negative): Unknown user id returns 404.
    Steps:
      1. GET /users/9999
    Expected: 404 + empty body.
    """

    @pytest.mark.negative
    def test_get_unknown_user_returns_404(self, reqres):
        response = reqres.get_user(9999)
        assert response.status_code == 404


@allure.feature("Users API")
@pytest.mark.api
class TestCreateUser:
    """
    USR-004: Create user echoes back submitted fields with server-assigned id + createdAt.
    Steps:
      1. POST /users with {name, job}
      2. Assert 201 + echoed payload + id present + createdAt present
    Expected: 201 with id and createdAt populated.
    """

    def test_create_user_returns_201_with_id(self, reqres):
        payload = {"name": "Ada Lovelace", "job": "Mathematician"}
        response = reqres.create_user(payload)
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == payload["name"]
        assert body["job"] == payload["job"]
        assert body["id"]
        assert body["createdAt"]
