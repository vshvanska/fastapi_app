from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY: str
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 300
    REFRESH_TOKEN_EXPIRE_DAYS = 1
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
