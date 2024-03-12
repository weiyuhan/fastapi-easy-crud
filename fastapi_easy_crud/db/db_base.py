import re

from sqlalchemy import TIMESTAMP, Column, Integer, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase  # type: ignore


class CommonBase(DeclarativeBase):
    id = Column(Integer, primary_key=True, index=True)
    # _uuid = Column(String(64), server_default=text("(uuid())"))
    create_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    last_modified_time = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        return name
