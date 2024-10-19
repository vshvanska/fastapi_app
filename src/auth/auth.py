import jwt

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jwt import InvalidTokenError
from src.auth.hasher import hasher
from src.auth.schemas import TokenData
from src.config import settings
from src.database import SessionLocal
from src.repositories import AbstractRepository


class Authenticator:

    async def authenticate_user(self, username: str, password: str,
                                repository: AbstractRepository,
                                session: SessionLocal):
        user = await repository.get_by_username(username, session)
        if not user:
            return False
        if not await hasher.verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    async def create_access_token(data: dict):
        to_encode = data.copy()
        expire = (datetime.now(timezone.utc) +
                  timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return {"access_token": encoded_jwt}

    @staticmethod
    async def decode_token(token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username = payload.get("sub")
            id = payload.get("id")
            if not username or not id:
                raise credentials_exception
            token_data = TokenData(username=username, id=id)
        except InvalidTokenError:
            raise credentials_exception
        return token_data

    async def get_current_user(self, token,
                               repository: AbstractRepository,
                               session: SessionLocal):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token_data = await self.decode_token(token)
        user = await repository.get_by_id(id=token_data.id, session=session)
        if user is None:
            raise credentials_exception
        return user
