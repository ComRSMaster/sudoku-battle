from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import UserORM
from backend.schemas.leaderboards import LeaderboardResponse, UserScoreSchema

router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])


@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboards(
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> LeaderboardResponse:
    """Получить глобальный лидерборд"""

    rank_stmt = (
        select(
            UserORM, func.rank().over(order_by=desc(UserORM.solved_count)).label("rank")
        )
        .order_by(desc(UserORM.solved_count))
        .limit(limit)
    )

    result = await db.execute(rank_stmt)
    leaderboard = []

    for user, rank in result.all():
        leaderboard.append(
            UserScoreSchema(
                user_id=user.user_id,
                username=user.username,
                name=user.name,
                photo_url=user.photo_url,
                solved_count=user.solved_count,
                rank=rank,
            )
        )

    return LeaderboardResponse(leaderboard=leaderboard)
