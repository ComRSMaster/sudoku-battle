from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import users as crud_users
from backend.database import get_db
from backend.schemas.users import UserCreateRequest, UserSchema, UserUpdateRequest
from core.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserSchema)
async def create_user_endpoint(
    payload: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """Создать нового пользователя"""
    try:
        user = await crud_users.create_user(
            db=db,
            user_id=payload.user_id,
            username=payload.username,
            name=payload.name,
            photo_url=payload.photo_url,
        )
        return UserSchema.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """Получить информацию о пользователе"""
    user = await crud_users.get_user(db, user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return UserSchema.model_validate(user)


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user_endpoint(
    user_id: int,
    payload: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """Обновить информацию о пользователе"""
    user = await crud_users.get_user(db, user_id)
    if not user:
        raise UserNotFoundError(user_id)

    if payload.name:
        user.name = payload.name
    if payload.photo_url is not None:
        user.photo_url = payload.photo_url

    await db.commit()
    await db.refresh(user)
    return UserSchema.from_orm(user)
