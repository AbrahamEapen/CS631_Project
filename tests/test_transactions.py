import pytest


def setup_user_and_account(client):
    # Register + login
    client.post("/auth/register", json={
        "username": "txnuser",
        "password": "txnpass"
    })

    login = client.post("/auth/login", json={
        "username": "txnuser",
        "password": "txnpass"
    })

    token = login.get_json()["access_token"]

    # Create account
    acc = client.post(
        "/user/accounts",
        json={"initial_balance": 1000},
        headers={"Authorization": f"Bearer {token}"}
    )

    account_id = acc.get_json()["account_number"]

    return token, account_id


def test_deposit(client):
    token, account_id = setup_user_and_account(client)

    response = client.post(
        "/transactions/deposit",
        json={"account_id": account_id, "amount": 200},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "transaction_id" in data or "message" in data


def test_withdraw(client):
    token, account_id = setup_user_and_account(client)

    response = client.post(
        "/transactions/withdraw",
        json={"account_id": account_id, "amount": 100},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_get_transactions(client):
    token, account_id = setup_user_and_account(client)

    response = client.get(
        f"/transactions/{account_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)