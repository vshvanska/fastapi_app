import pytest

from datetime import datetime
from sqlalchemy import insert
from conftest import client, TestingSessionLocal
from src.auth.hasher import hasher
from src.auth.models import User


@pytest.fixture
async def add_user():
    async with TestingSessionLocal() as session:
        stmt = insert(User).values(username='username12',
                                   email="useremail12@example.com",
                                   hashed_password=await hasher.hash("StrongPass1!"))
        await session.execute(stmt)
        await session.commit()


def test_register_user_success():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "StrongPass1!",
        "password_confirm": "StrongPass1!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 201


def test_register_user_different_passwords():
    user_data = {
        "username": "testuser",
        "email": "test1@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "StrongPass1!",
        "password_confirm": "StrongPass2!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_user_passwords_len_less_than_8():
    user_data = {
        "username": "testuser2",
        "email": "test1@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "Stron1",
        "password_confirm": "Stron1"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_user_passwords_without_upper_letter():
    user_data = {
        "username": "testuser2",
        "email": "test1@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "strongpassword1!",
        "password_confirm": "strongpassword1!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_user_passwords_without_lower_letter():
    user_data = {
        "username": "testuser2",
        "email": "test1@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "STRONGPAS1!",
        "password_confirm": "STRONGPAS1!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_passwords_without_digit():
    user_data = {
        "username": "testuser2",
        "email": "test1@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "StrongPass!",
        "password_confirm": "StrongPass!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_user_with_exiting_email(add_user):
    user_data = {
        "username": "testuser2",
        "email": "useremail12@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "StrongPass!",
        "password_confirm": "StrongPass!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_user_with_exiting_username():
    user_data = {
        "username": "username12",
        "email": "user@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "StrongPass!",
        "password_confirm": "StrongPass!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_user_with_birth_date_in_future():
    today = datetime.now().year
    user_data = {
        "username": "username",
        "email": "user@example.com",
        "fullname": "Test User",
        "birthdate": f"{today + 1}-01-01",
        "password": "StrongPass1!",
        "password_confirm": "StrongPass1!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_user_login_success():
    user_data = {
        "username": "username12",
        "password": "StrongPass1!"
    }
    response = client.post("/users/token", data=user_data)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data.get("access_token") is not None


def test_user_login_invalid_username():
    user_data = {
        "username": "invalidusername",
        "password": "StrongPass1!"
    }
    response = client.post("/users/token", data=user_data)
    response_data = response.json()
    assert response.status_code == 401
    assert response_data.get("access_token") is None


def test_user_login_invalid_password():
    user_data = {
        "username": "username",
        "password": "StrongPass11!"
    }
    response = client.post("/users/token", data=user_data)
    response_data = response.json()
    assert response.status_code == 401
    assert response_data.get("access_token") is None


def test_read_users_me_success():
    user_data = {
        "username": "username12",
        "password": "StrongPass1!"
    }
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {login_response_data.get('access_token')}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("username") == user_data["username"]


def test_read_users_me_unauthorized():
    response = client.get("/users/me")
    assert response.status_code == 401


def test_read_users_me_invalid_token():
    response = client.get(
        "/users/me", headers={"Authorization": "Bearer dfgzdg.ihausfi7.kuyfgiufyo"}
    )
    assert response.status_code == 401
