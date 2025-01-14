import re

from datetime import date
from typing import Optional
from pydantic import EmailStr, field_validator, BaseModel, model_validator, ConfigDict
from src.schemas import BaseInstance


class UserBase(BaseModel):
    username: str
    email: EmailStr
    fullname: Optional[str] = None
    birthdate: Optional[date] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    password_confirm: str

    @field_validator("password")
    @classmethod
    def valid_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")

        return value

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("birthdate")
    @classmethod
    def validate_birth_date(cls, value: Optional[date]) -> Optional[date]:
        if value is not None:
            today = date.today()
            if value > today:
                raise ValueError("Birth date cannot be in the future.")
        return value


class User(UserBase, BaseInstance):
    id: int


class UserLogin(BaseModel):
    username: str
    password: str


class UserPost(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class AccessToken(BaseModel):
    access: str
    token_type: str = "bearer"


class TokenPair(BaseModel):
    access: str
    refresh: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
    id: int | None = None
    type: str | None = None
