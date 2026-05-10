from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from core.constants import DEFAULT_HOLES_COUNT, DEFAULT_REG_SIZE

game_users = Table(
    "game_users",
    Base.metadata,
    Column(
        "user_id", ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    ),
    Column("game_id", ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
)


class UserORM(Base):
    """ORM модель пользователя в базе данных"""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(32), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255))
    photo_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    solved_count: Mapped[int] = mapped_column(default=0)
    fastest_solve_time: Mapped[Optional[int]] = mapped_column(nullable=True)
    achievements: Mapped[dict] = mapped_column(JSONB, default=dict)

    games: Mapped[List[GameORM]] = relationship(
        secondary=game_users, back_populates="users"
    )


class GameORM(Base):
    """ORM модель игры в судоку"""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    n: Mapped[int] = mapped_column(default=DEFAULT_REG_SIZE)
    holes_count: Mapped[int] = mapped_column(default=DEFAULT_HOLES_COUNT)
    table: Mapped[list] = mapped_column(JSONB)
    holes_mask: Mapped[list] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    users: Mapped[List[UserORM]] = relationship(
        secondary=game_users, back_populates="games"
    )
