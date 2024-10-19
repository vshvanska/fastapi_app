from datetime import date
from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.models import BaseModel


class User(BaseModel):
    __tablename__ = "user_account"

    username: Mapped[str] = mapped_column(String(30), unique=True)
    fullname: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    birthdate: Mapped[Optional[date]]
    hashed_password: Mapped[str] = mapped_column(String)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return {self.username}
