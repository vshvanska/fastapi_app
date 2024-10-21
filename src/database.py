from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

DATABASE_URL = (f"postgresql+asyncpg://{settings.db.DB_USER}:{settings.db.DB_PASSWORD}@"
                f"{settings.db.DB_HOST}:{settings.db.DB_PORT}/{settings.db.DB_NAME}")

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


Base = declarative_base()
metadata = MetaData()
