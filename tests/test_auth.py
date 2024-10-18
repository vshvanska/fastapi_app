import pytest

from datetime import datetime
from sqlalchemy import insert
from conftest import client, TestingSessionLocal
from src.auth.models import User


@pytest.fixture
async def add_user():
    async with TestingSessionLocal() as session:
        stmt = insert(User).values(username='username',
                                   email="useremail@example.com",
                                   hashed_password=hash("StrongPass1!"))
        await session.execute(stmt)


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
        "email": "useremail@example.com",
        "fullname": "Test User",
        "birthdate": "2000-01-01",
        "password": "StrongPass!",
        "password_confirm": "StrongPass!"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_register_user_with_exiting_username(add_user):
    user_data = {
        "username": "username",
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
