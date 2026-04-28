import pytest


def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpass"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert "user_id" in data or "message" in data


def test_login_user(client):
    # First register user
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "loginpass"
    })

    # Then login
    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "loginpass"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "user" in data