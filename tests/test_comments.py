import pytest
from sqlalchemy import insert, select
from src.auth.hasher import hasher
from src.auth.models import User
from src.posts.models import Post
from tests.conftest import TestingSessionLocal, client

userdata = {
    "username": "user",
    "email": "usergmail@example.com",
    "password": "StrongPass1!",
}


@pytest.fixture
async def add_user():
    async with TestingSessionLocal() as session:
        stmt = insert(User).values(
            username=userdata["username"],
            email=userdata["email"],
            hashed_password=await hasher.hash(userdata["password"]),
        )
        await session.execute(stmt)
        await session.commit()


@pytest.fixture
async def add_post():
    async with TestingSessionLocal() as session:
        user = await session.scalars(select(User).where(User.username == "user"))
        user = user.first()
        stmt = insert(Post).values(
            title="Test Post",
            content="This is a test post.",
            user_id=user.id,
        )
        result = await session.execute(stmt)
        await session.commit()

        post_id = result.inserted_primary_key[0]
        return post_id


def test_create_comment_success(add_user, add_post):
    comment_data = {
        "content": "My Test Comment",
    }
    user_data = {"username": userdata["username"], "password": userdata["password"]}
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()
    post_response = client.get(
        "/posts/my",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
    )
    post_id = int(post_response.json()[0]["id"])
    comment_data["post_id"] = post_id

    response = client.post(
        "/comments",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json=comment_data,
    )
    assert response.status_code == 200


def test_create_comment_unauthorized(add_post):
    post_id = add_post
    comment_data = {"content": "My Test Comment"}
    comment_data["post_id"] = post_id

    response = client.post("/comments", json=comment_data)
    assert response.status_code == 401


def test_get_list_comments_success(add_post):
    post_id = add_post
    comment_data = {"content": "My Test Comment", "post_id": post_id}

    user_data = {"username": userdata["username"], "password": userdata["password"]}
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()

    client.post(
        "/comments",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json=comment_data,
    )

    response = client.get(f"/comments?post_id={post_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_personal_comments():
    user_data = {"username": userdata["username"], "password": userdata["password"]}
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()
    response = client.get(
        "/comments/my",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
    )
    assert response.status_code == 200
    for comment in response.json():
        assert comment["user"]["username"] == user_data["username"]


def test_personal_comment_unathorized():
    response = client.get("/comments/my")
    assert response.status_code == 401


def test_update_comment_success(add_post):
    post_id = add_post
    comment_data = {
        "content": "My Test Comment",
        "post_id": post_id,
    }
    new_content = {"content": "New"}
    user_data = {"username": userdata["username"], "password": userdata["password"]}
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()

    create_response = client.post(
        "/comments",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json=comment_data,
    )
    comment_id = create_response.json()["id"]

    response = client.put(
        f"/comments/{comment_id}",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json=new_content,
    )

    assert response.status_code == 200
    assert response.json().get("content") == new_content["content"]


def test_update_comment_unathorized():
    new_content = {"content": "New"}
    response = client.put(
        "/comments/3",
        json=new_content,
    )

    assert response.status_code == 401


def test_update_comment_does_not_exist():
    new_content = {"content": "New"}
    user_data = {"username": userdata["username"], "password": userdata["password"]}
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()

    response = client.put(
        "/comments/1000",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json=new_content,
    )

    assert response.status_code == 404


def test_delete_comment_success(add_post):
    post_id = add_post
    comment_data = {
        "content": "My Test Comment",
        "post_id": post_id,
    }

    user_data = {"username": userdata["username"], "password": userdata["password"]}
    login_response = client.post("/users/token", data=user_data)
    login_response_data = login_response.json()

    create_response = client.post(
        "/comments",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
        json=comment_data,
    )
    comment_id = create_response.json()["id"]

    response = client.delete(
        f"/comments/{comment_id}",
        headers={"Authorization": f"Bearer {login_response_data.get('access')}"},
    )

    assert response.status_code == 204
