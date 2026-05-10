from aiogram.utils.web_app import WebAppUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import UserORM
from core.exceptions import UserNotFoundError


async def get_user(db: AsyncSession, user_id: int) -> UserORM | None:
    """Получить пользователя по ID"""
    result = await db.execute(select(UserORM).where(UserORM.user_id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> UserORM | None:
    """Получить пользователя по username"""
    result = await db.execute(select(UserORM).where(UserORM.username == username))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    user_id: int,
    username: str | None,
    name: str,
    photo_url: str | None,
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
    user_data: WebAppUser,
) -> UserORM:
    """Получить пользователя или создать с данными по умолчанию"""
    user = await get_user(db, user_data.id)
    if user:
        return user

    full_name = (
        f"{user_data.first_name} {user_data.last_name}"
        if user_data.last_name
        else user_data.first_name
    )

    return await create_user(
        db, user_data.id, user_data.username, full_name, user_data.photo_url
    )


async def increment_user_solved_count(db: AsyncSession, user_id: int) -> int:
    """Увеличить количество разгаданных судоку"""
    user = await get_user(db, user_id)
    if not user:
        raise UserNotFoundError(user_id)

    user.solved_count += 1
    await db.commit()
    await db.refresh(user)
    return user.solved_count
