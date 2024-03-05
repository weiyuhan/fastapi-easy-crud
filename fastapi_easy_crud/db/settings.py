import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_engine: Optional[str]
    sqlalchemy_engine_password: Optional[str]


settings = Settings


def init(
    sqlalchemy_engine: Optional[str] = None,
    sqlalchemy_engine_password: Optional[str] = None,
) -> None:
    global settings
    settings.sqlalchemy_engine = sqlalchemy_engine or os.getenv("SQLALCHEMY_ENGINE")
    settings.sqlalchemy_engine_password = sqlalchemy_engine_password or os.getenv(
        "SQLALCHEMY_ENGINE_PASSWORD"
    )
    # settings = Settings(sqlalchemy_engine=sqlalchemy_engine, sqlalchemy_engine_password=sqlalchemy_engine_password)
