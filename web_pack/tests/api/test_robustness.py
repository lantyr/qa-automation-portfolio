"""
Suite: API robustness
Cross-cutting concerns: response time, content-type, idempotency, and graceful degradation.
"""
import allure
import pytest


@allure.feature("Robustness")
@pytest.mark.api
class TestRobustness:
    """
    RBS-001: Healthy endpoint responds under 3 seconds.
    Steps:
      1. GET /users?page=1
      2. Assert elapsed < 3s
    Expected: response within 3s wall clock.
    """

    def test_list_users_responds_under_3s(self, reqres):
        response = reqres.list_users()
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < 3.0, (
            f"Expected <3s, got {response.elapsed.total_seconds()}s"
        )

    """
    RBS-002: JSON endpoints declare application/json content-type.
    Steps:
      1. GET /users/1
      2. Assert Content-Type header
    Expected: starts with "application/json".
    """

    def test_users_endpoint_returns_json_content_type(self, reqres):
        response = reqres.get_user(1)
        assert response.headers["Content-Type"].startswith("application/json")

    """
    RBS-003 (idempotency): Repeated GETs return identical payload.
    Steps:
      1. GET /users/2 twice
      2. Compare JSON bodies
    Expected: bodies are byte-identical.
    """

    def test_get_user_is_idempotent(self, reqres):
        first = reqres.get_user(2).json()
        second = reqres.get_user(2).json()
        assert first == second

    """
    RBS-004 (negative): Invalid id still produces a defined non-5xx response.
    Steps:
      1. GET /users/<bad_id> for three invalid values
    Expected: 404 or 400, NOT 5xx.
    """

    @pytest.mark.negative
    @pytest.mark.parametrize("bad_id", ["abc", "-1", "0"])
    def test_invalid_id_graceful_degradation(self, reqres, bad_id):
        response = reqres.session.get(
            f"{reqres.base_url}/users/{bad_id}", timeout=reqres.timeout
        )
        assert response.status_code < 500, (
            f"Server should not 5xx on bad id, got {response.status_code}"
        )
