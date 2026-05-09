"""API для управления лидербордом"""

from pydantic import BaseModel
from fastapi import APIRouter, Query


class UserScoreSchema(BaseModel):
    """Схема для пользователя в лидербoрдe"""

    user_id: int
    solved_count: int
    rank: int


class LeaderboardResponse(BaseModel):
    """Схема ответа лидерборда"""

    leaderboard: list[UserScoreSchema]


# TODO: заменить на PostgreSQL
_user_scores: dict[int, int] = {}


def increment_user_score(user_id: int) -> int:
    """Увеличить количество разгаданных судоку для пользователя"""
    if user_id not in _user_scores:
        _user_scores[user_id] = 0
    _user_scores[user_id] += 1
    return _user_scores[user_id]


def get_user_score(user_id: int) -> int:
    """Получить количество разгаданных судоку для пользователя"""
    return _user_scores.get(user_id, 0)


def get_leaderboard(limit: int = 100) -> list[UserScoreSchema]:
    """Получить лидерборд с рейтингом пользователей"""
    sorted_scores = sorted(
        _user_scores.items(), key=lambda x: x[1], reverse=True
    )

    leaderboard = []
    for rank, (user_id, solved_count) in enumerate(sorted_scores[:limit], 1):
        leaderboard.append(
            UserScoreSchema(user_id=user_id, solved_count=solved_count, rank=rank)
        )

    return leaderboard


router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])


@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboards(limit: int = Query(default=100, ge=1, le=1000)) -> LeaderboardResponse:
    """Получить глобальный лидерборд"""
    return LeaderboardResponse(leaderboard=get_leaderboard(limit))


@router.get("/user/{user_id}")
async def get_user_leaderboard_position(user_id: int) -> UserScoreSchema:
    """Получить позицию пользователя в лидербorde"""
    leaderboard = get_leaderboard(limit=10000)

    for entry in leaderboard:
        if entry.user_id == user_id:
            return entry

    return UserScoreSchema(
        user_id=user_id,
        solved_count=get_user_score(user_id),
        rank=len(leaderboard) + 1 if leaderboard else 1
    )
