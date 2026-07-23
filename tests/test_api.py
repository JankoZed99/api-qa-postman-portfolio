from fastapi.testclient import TestClient

from app.main import DEMO_TOKEN, app


client = TestClient(app)
AUTH = {"Authorization": f"Bearer {DEMO_TOKEN}"}


def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}


def test_valid_login_returns_bearer_token():
    response = client.post(
        "/auth/login",
        json={"email": "qa@example.test", "password": "qa-demo-2026"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == DEMO_TOKEN
    assert response.json()["token_type"] == "bearer"


def test_invalid_login_is_rejected():
    response = client.post(
        "/auth/login",
        json={"email": "qa@example.test", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_missing_login_field_returns_validation_error():
    response = client.post("/auth/login", json={"email": "qa@example.test"})
    assert response.status_code == 422


def test_protected_route_requires_token():
    response = client.get("/users")
    assert response.status_code == 401


def test_users_pagination_contract():
    response = client.get("/users?page=1&page_size=2", headers=AUTH)
    payload = response.json()
    assert response.status_code == 200
    assert len(payload["items"]) == 2
    assert payload["pagination"] == {"page": 1, "page_size": 2, "total": 3}


def test_page_zero_is_rejected():
    response = client.get("/users?page=0", headers=AUTH)
    assert response.status_code == 422


def test_unknown_user_returns_404():
    response = client.get("/users/999", headers=AUTH)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_task_returns_documented_status_and_body():
    response = client.post(
        "/tasks",
        headers=AUTH,
        json={"title": "Verify release candidate", "priority": "high"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 101,
        "title": "Verify release candidate",
        "priority": "high",
        "status": "open",
    }


def test_short_task_title_is_rejected():
    response = client.post(
        "/tasks",
        headers=AUTH,
        json={"title": "x", "priority": "low"},
    )
    assert response.status_code == 422


def test_delete_task_returns_204_without_body():
    response = client.delete("/tasks/101", headers=AUTH)
    assert response.status_code == 204
    assert response.content == b""

