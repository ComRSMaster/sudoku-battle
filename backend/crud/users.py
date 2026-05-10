from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import UserORM
from core.exceptions import UserNotFoundError


async def get_user(db: AsyncSession, user_id: int) -> Optional[UserORM]:
    """Получить пользователя по ID"""
    result = await db.execute(select(UserORM).where(UserORM.user_id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserORM]:
    """Получить пользователя по username"""
    result = await db.execute(select(UserORM).where(UserORM.username == username))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    user_id: int,
    username: Optional[str],
    name: str,
    photo_url: Optional[str] = None,
) -> UserORM:
    """Создать нового пользователя"""
    user = UserORM(
        user_id=user_id,
        username=username,
        name=name,
        photo_url=photo_url,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_or_create(
    db: AsyncSession,
    user_id: int,
    username: Optional[str] = None,
    name: str = "",
) -> UserORM:
    """Получить пользователя или создать с данными по умолчанию"""
    user = await get_user(db, user_id)
    if user:
        return user

    username = username or f"user_{user_id}"
    name = name or f"User {user_id}"

    return await create_user(db, user_id, username, name)


async def increment_user_solved_count(db: AsyncSession, user_id: int) -> int:
    """Увеличить количество разгаданных судоку"""
    user = await get_user(db, user_id)
    if not user:
        raise UserNotFoundError(user_id)

    user.solved_count += 1
    await db.commit()
    await db.refresh(user)
    return user.solved_count
