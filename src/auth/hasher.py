from src.config import settings


class Hasher:
    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str):
        return settings.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def hash(password: str) -> str:
        return settings.pwd_context.hash(password)


hasher = Hasher()
