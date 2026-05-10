from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import get_user_data_from_tma
from backend.database import get_db
from backend.models import GameORM, UserORM


class GameHistorySchema(BaseModel):
    game_id: int
    created_at: str
    holes_count: int


router = APIRouter(prefix="/games", tags=["Games"])


@router.get("/history")
async def get_user_history(
    tma: str | None = Query(None), db: AsyncSession = Depends(get_db)
) -> List[GameHistorySchema]:
    user_data = get_user_data_from_tma(tma)

    stmt = (
        select(GameORM)
        .join(GameORM.users)
        .where(UserORM.user_id == user_data.id)
        .order_by(GameORM.created_at.desc())
    )
    result = await db.execute(stmt)
    games = result.scalars().all()

    return [
        GameHistorySchema(
            game_id=g.id, created_at=str(g.created_at), holes_count=g.holes_count
        )
        for g in games
    ]
