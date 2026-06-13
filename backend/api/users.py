from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import get_user_data_from_tma
from backend.crud import users as crud_users
from backend.database import get_db
from backend.schemas.users import UserSchema
from core.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserSchema)
async def get_user_endpoint(
    tma: str | None = Query(None),
    user_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """Получить информацию о конкретном пользователе, если не указан `user_id`, то о себе"""

    user_data = get_user_data_from_tma(tma)

    if user_id is None:
        user_id = user_data.id
        user = await crud_users.get_user_or_create(db, user_data)
    else:
        user = await crud_users.get_user(db, user_id)
        if not user:
            raise UserNotFoundError(user_id)
    return UserSchema.model_validate(user)
