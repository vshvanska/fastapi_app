import pytest
from datetime import date
from sqlalchemy import insert, delete
from src.auth.hasher import hasher
from src.auth.models import User
from src.comments.models import Comment
from src.posts.models import Post
from tests.conftest import TestingSessionLocal, client

userdata = {
    "username": "analytics_user",
    "email": "usera@example.com",
    "password": "StrongPass1!",
}

first_comment = {
    "content": "first_comment",
    "is_active": True,
    "created_at": date(2024, 10, 20),
}
second_comment = {
    "content": "second_comment",
    "is_active": False,
    "created_at": date(2024, 10, 15),
}
third_comment = {
    "content": "third_comment",
    "is_active": False,
    "created_at": date(2024, 10, 17),
}
last_comment = {
    "content": "last_comment",
    "is_active": True,
    "created_at": date(2024, 10, 10),
}

comments = [first_comment, second_comment, third_comment, last_comment]


@pytest.fixture
async def add_user():
    async with TestingSessionLocal() as session:
        stmt = insert(User).values(
            username=userdata["username"],
            email=userdata["email"],
            hashed_password=await hasher.hash(userdata["password"]),
        )
        user = await session.execute(stmt)
        await session.commit()
        return user.inserted_primary_key[0]


@pytest.fixture
async def add_post_and_comments(add_user):
    user_id = add_user
    async with TestingSessionLocal() as session:
        stmt = insert(Post).values(
            title="Test Post",
            content="This is a test post.",
            user_id=user_id,
        )
        result = await session.execute(stmt)
        post_id = result.inserted_primary_key[0]
        comments_to_delete = delete(Comment)
        await session.execute(comments_to_delete)
        for comment in comments:
            new_comment = insert(Comment).values(
                content=comment["content"],
                is_active=comment["is_active"],
                created_at=comment["created_at"],
                user_id=user_id,
                post_id=post_id,
            )
            await session.execute(new_comment)
        await session.commit()
        return post_id


def test_get_analytics_success(add_post_and_comments):
    response = client.get(
        "/analytics/comments-daily-breakdown",
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("total_comments", 0) == 4
    assert response_data.get("active_comments", 0) == 2
    assert response_data.get("blocked_comments", 0) == 2


def test_get_analytics_date_from():
    response = client.get(
        "/analytics/comments-daily-breakdown?date_from=2024-10-15",
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("total_comments", 0) == 3
    assert response_data.get("active_comments", 0) == 1
    assert response_data.get("blocked_comments", 0) == 2


def test_get_analytics_date_to():
    response = client.get(
        "/analytics/comments-daily-breakdown?date_to=2024-10-15",
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("total_comments", 0) == 1
    assert response_data.get("active_comments", 0) == 1
    assert response_data.get("blocked_comments", 0) == 0


def test_get_analytics_date_to_date_from():
    response = client.get(
        "/analytics/comments-daily-breakdown?date_to=2024-10-20&date_from=2024-10-15",
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("total_comments", 0) == 2
    assert response_data.get("active_comments", 0) == 0
    assert response_data.get("blocked_comments", 0) == 2
