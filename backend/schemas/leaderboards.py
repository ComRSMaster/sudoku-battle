from pydantic import BaseModel

from .users import UserSchema


class UserScoreSchema(UserSchema):
    """Схема для пользователя в лидербoрдe"""

    rank: int


class LeaderboardResponse(BaseModel):
    """Схема ответа лидерборда"""

    leaderboard: list[UserScoreSchema]
