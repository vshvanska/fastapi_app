import os

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic.v1 import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class DB_Settings(BaseSettings):
    DB_HOST: str = os.environ.get('DB_HOST')
    DB_PORT: int = os.environ.get('DB_PORT')
    DB_USER: str = os.environ.get('DB_USER')
    DB_PASSWORD: str = os.environ.get('DB_PASSWORD')
    DB_NAME: str = os.environ.get('DB_NAME')


class Celery_settings(BaseSettings):
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND")


class Settings(BaseSettings):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 300
    REFRESH_TOKEN_EXPIRE_DAYS = 1
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
    AI_API_KEY: str = os.environ.get("AI_API_KEY")
    celery: Celery_settings = Celery_settings()
    db: DB_Settings = DB_Settings()

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
