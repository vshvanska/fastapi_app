import re

from datetime import datetime, date
from typing import Optional
from pydantic import EmailStr, field_validator, BaseModel, model_validator


class BaseInstance(BaseModel):
    created_at: datetime
    updated_at: datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    fullname: str = None
    birthdate: date = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    password_confirm: str

    @field_validator("password")
    @classmethod
    def valid_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError(
               'Password must be at least 8 characters long'
            )

        if not re.search(r'[A-Z]', value):
            raise ValueError(
                'Password must contain at least one uppercase letter'
            )

        if not re.search(r'[a-z]', value):
            raise ValueError(
                'Password must contain at least one lowercase letter'
            )

        if not re.search(r'[0-9]', value):
            raise ValueError('Password must contain at least one digit')

        return value

    @model_validator(mode='after')
    def passwords_match(self) -> 'UserCreate':
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

    @field_validator('birthdate')
    @classmethod
    def validate_birth_date(cls, value: Optional[date]) -> Optional[date]:
        if value is not None:
            today = date.today()
            if value > today:
                raise ValueError("Birth date cannot be in the future.")
        return value
