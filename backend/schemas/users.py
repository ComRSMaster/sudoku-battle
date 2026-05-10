from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    """Схема пользователя для API"""

    user_id: int
    username: Optional[str] = None
    name: str
    photo_url: Optional[str] = None
    solved_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    """Запрос для создания пользователя"""

    user_id: int
    username: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    photo_url: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """Запрос для обновления пользователя"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    photo_url: Optional[str] = None
