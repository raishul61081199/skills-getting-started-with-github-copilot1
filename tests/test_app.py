import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Tennis Club" in data
    assert "participants" in data["Tennis Club"]

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Tennis Club/signup", params={"email": "test@example.com"})
    assert response.status_code == 200
    assert "Signed up test@example.com for Tennis Club" in response.json()["message"]

    # Check that participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Tennis Club"]["participants"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Volleyball Team/signup", params={"email": "duplicate@example.com"})
    # Second signup should fail
    response = client.post("/activities/Volleyball Team/signup", params={"email": "duplicate@example.com"})
    assert response.status_code == 400
    assert "Student already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent Activity/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_from_activity():
    # First signup
    client.post("/activities/Music Band/signup", params={"email": "unregister@example.com"})
    # Then unregister
    response = client.delete("/activities/Music Band/unregister", params={"email": "unregister@example.com"})
    assert response.status_code == 200
    assert "Unregistered unregister@example.com from Music Band" in response.json()["message"]

    # Check that participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Music Band"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Photography Club/unregister", params={"email": "notsigned@example.com"})
    assert response.status_code == 400
    assert "Student not signed up" in response.json()["detail"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent Activity/unregister", params={"email": "test@example.com"})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect to static, but in test client it might serve directly
    # Actually, the redirect is to /static/index.html, but since static is mounted, it should work