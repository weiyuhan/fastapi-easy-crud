from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
engine = create_engine(
    engine_url,
    pool_pre_ping=True,
    poolclass=NullPool,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
