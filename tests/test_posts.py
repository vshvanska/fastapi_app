import pytest

from sqlalchemy import insert
from conftest import client, TestingSessionLocal
from src.auth.hasher import hasher
from src.auth.models import User
from src.posts.models import Post


test_user1_data = {
    "username": "username123",
    "email": "useremail123@example.com",
    "password": "StrongPass1!",
}
test_user2_data = {
    "username": "flyronik",
    "email": "flyronik@example.com",
    "password": "StrongPass2!",
}
test_post1_data = {"title": "My First Post", "content": "Just content"}
test_post2_data = {"title": "My Second Post", "content": "Just content"}


@pytest.fixture
async def add_users_and_posts():
    async with TestingSessionLocal() as session:
        stmt = insert(User).values(
            username=test_user1_data["username"],
            email=test_user1_data["email"],
            hashed_password=await hasher.hash(test_user1_data["password"]),
        )
        result = await session.execute(stmt)
        user1_id = result.inserted_primary_key[0]

        stmt = insert(User).values(
            username=test_user2_data["username"],
            email=test_user2_data["email"],
            hashed_password=await hasher.hash(test_user2_data["password"]),
        )
        result = await session.execute(stmt)
        user2_id = result.inserted_primary_key[0]

        test_post_1 = {
            "title": test_post1_data["title"],
            "content": test_post1_data["content"],
            "user_id": user1_id,
        }
        test_post_2 = {
            "title": test_post2_data["title"],
            "content": test_post2_data["content"],
            "user_id": user2_id,
        }

        stmt = insert(Post).values(test_post_1)
        await session.execute(stmt)

        stmt = insert(Post).values(test_post_2)
        await session.execute(stmt)
        await session.commit()


def test_create_post_success(add_users_and_posts):
    post_data = {
        "title": "My Test Post",
        "content": "This is the content of my first post.",
    }
    user_data = {"username": "username123", "password": "StrongPass1!"}
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()
    response = client.post(
        "/posts",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json=post_data,
    )
    assert response.status_code == 200


def test_create_post_unauthorized():
    post_data = {
        "title": "My first Post",
        "content": "This is the content of my first post.",
    }

    response = client.post("/posts", json=post_data)
    assert response.status_code == 401


def test_get_posts_success():
    response = client.get("/posts")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0


def test_get_posts_by_username():
    response = client.get(f"/posts?username={test_user2_data['username']}")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1


def test_get_posts_by_title():
    response = client.get(f"/posts?title={test_post1_data['title']}")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1


def test_get_personal_posts_success():
    login_response = client.post(
        "/users/token",
        data={
            "username": test_user2_data["username"],
            "password": test_user2_data["password"],
        },
    )
    login_response_data = login_response.json()
    response = client.get(
        "/posts/my",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1


def test_get_personal_posts_unauthorized():
    response = client.get("/posts/my")
    assert response.status_code == 401


def test_update_and_delete_post_success():
    login_response = client.post(
        "/users/token",
        data={
            "username": test_user2_data["username"],
            "password": test_user2_data["password"],
        },
    )
    assert login_response.status_code == 200
    login_response_data = login_response.json()

    response = client.get(
        "/posts/my",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
    )
    assert response.status_code == 200

    post_id = int(response.json()[0]["id"])
    response = client.put(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json={"title": "New title", "content": "New content"},
    )
    assert response.status_code == 200

    response = client.get(
        "/posts/my",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
    )
    assert response.status_code == 200

    updated_title = response.json()[0]["title"]
    assert updated_title == "New title"

    response = client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
    )
    assert response.status_code == 204
