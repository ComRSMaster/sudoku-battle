from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from backend.models import GameORM, UserORM
from core.exceptions import UserNotFoundError
from core.generator import Sudoku


async def create_game(db: AsyncSession, user_id: int, holes_count: int) -> GameORM:
    """Создать новую игру и привязать к пользователю"""
    sudoku = Sudoku(holes_count=holes_count)

    user = await db.get(UserORM, user_id)
    if not user:
        raise UserNotFoundError(user_id)

    game = GameORM(
        n=sudoku.n,
        holes_count=sudoku.holes_count,
        table=sudoku.table,
    )
    if user:
        game.users.append(user)

    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game


async def get_game(db: AsyncSession, game_id: int) -> Optional[GameORM]:
    """Получить игру по ID с загрузкой пользователей"""
    result = await db.execute(
        select(GameORM)
        .where(GameORM.id == game_id)
        .options(selectinload(GameORM.users))
    )
    return result.scalars().first()


async def update_game_table(
    db: AsyncSession, game_id: int, table: list, holes_count: int
) -> None:
    """Обновить состояние игрового поля"""
    game = await get_game(db, game_id)
    if not game:
        return

    game.table = table
    flag_modified(game, "table") 
    game.holes_count = holes_count
    await db.commit()


async def delete_game(db: AsyncSession, game_id: int) -> bool:
    """Удалить игру"""
    game = await get_game(db, game_id)
    if not game:
        return False

    await db.delete(game)
    await db.commit()
    return True
