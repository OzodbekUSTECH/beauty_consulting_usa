from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import Base


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[str]
    name: Mapped[Optional[str]]
    username: Mapped[Optional[str]]
    phone_number: Mapped[Optional[str]]
    thread_id: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)