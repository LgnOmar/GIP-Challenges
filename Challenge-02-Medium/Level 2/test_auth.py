import os
import pytest
import datetime
from fastapi.testclient import TestClient

# Use a test database
TEST_DB = "test_auth.db"
os.environ["DB_PATH"] = TEST_DB

from main import app, init_db, create_access_token

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Remove existing test db if any, and initialize fresh
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_signup_success():
    response = client.post("/signup", json={"email": "user@example.com", "password": "securepassword123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
    assert "created_at" in data

def test_signup_duplicate_email():
    client.post("/signup", json={"email": "user@example.com", "password": "securepassword123"})
    response = client.post("/signup", json={"email": "user@example.com", "password": "anotherpassword"})
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]

def test_signup_invalid_input():
    # Invalid email format
    res1 = client.post("/signup", json={"email": "not-an-email", "password": "securepassword123"})
    assert res1.status_code == 422

    # Password too short (< 6 characters)
    res2 = client.post("/signup", json={"email": "user@example.com", "password": "123"})
    assert res2.status_code == 422

def test_login_success():
    client.post("/signup", json={"email": "user@example.com", "password": "securepassword123"})
    response = client.post("/login", json={"email": "user@example.com", "password": "securepassword123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    client.post("/signup", json={"email": "user@example.com", "password": "securepassword123"})

    # Wrong password
    res1 = client.post("/login", json={"email": "user@example.com", "password": "wrongpassword"})
    assert res1.status_code == 401

    # Non-existent user
    res2 = client.post("/login", json={"email": "unknown@example.com", "password": "securepassword123"})
    assert res2.status_code == 401

def test_protected_me_endpoint_success():
    signup_res = client.post("/signup", json={"email": "user@example.com", "password": "securepassword123"})
    user_id = signup_res.json()["id"]

    login_res = client.post("/login", json={"email": "user@example.com", "password": "securepassword123"})
    token = login_res.json()["access_token"]

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "user@example.com"

def test_protected_me_missing_token():
    response = client.get("/me")
    assert response.status_code == 403 or response.status_code == 401

def test_protected_me_invalid_token():
    response = client.get("/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

def test_protected_me_expired_token():
    client.post("/signup", json={"email": "user@example.com", "password": "securepassword123"})
    expired_token = create_access_token(
        {"sub": "1", "email": "user@example.com"},
        expires_delta=datetime.timedelta(seconds=-10),
    )
    response = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()
