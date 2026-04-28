import pytest


def get_token(client):
    client.post("/auth/register", json={
        "username": "acctuser",
        "password": "acctpass"
    })

    res = client.post("/auth/login", json={
        "username": "acctuser",
        "password": "acctpass"
    })

    return res.get_json()["access_token"]


def test_create_account(client):
    token = get_token(client)

    response = client.post(
        "/user/accounts",
        json={"initial_balance": 500},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "account_number" in data


def test_get_accounts(client):
    token = get_token(client)

    response = client.get(
        "/user/accounts",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_profile(client):
    token = get_token(client)

    response = client.get(
        "/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "username" in data