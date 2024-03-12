from typing import AsyncGenerator
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import NullPool

from fastapi_easy_crud.db.settings import settings

engine_base_url = settings.sqlalchemy_engine
password = settings.sqlalchemy_engine_password
if not engine_base_url:
    raise ValueError("SQLALCHEMY_ENGINE environment variable is empty")
if not password:
    raise ValueError("SQLALCHEMY_ENGINE_PASSWORD environment variable is empty")
password_encoded = quote_plus(password)  # type: ignore
engine_url = engine_base_url % password_encoded

engine = create_async_engine(
    engine_url,
    pool_pre_ping=True,
    poolclass=NullPool,
    pool_recycle=3600,
)


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with get_async_session_maker()() as session:
            yield session
    finally:
        pass
