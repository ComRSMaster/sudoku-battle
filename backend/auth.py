from aiogram.utils.web_app import (
    WebAppInitData,
    WebAppUser,
    safe_parse_webapp_init_data,
)

from core.config import settings
from core.exceptions import AuthTMAError


def get_user_data_from_tma(tma_data: str | None) -> WebAppUser:
    """Извлекает информацию о пользователе из initData Telegram Mini Apps."""
    if not tma_data:
        # TODO: raise AuthTMAError("Missing tma data")
        return WebAppUser(id=1, first_name="Name")

    try:
        data: WebAppInitData = safe_parse_webapp_init_data(
            token=settings.bot_token, init_data=tma_data
        )
        if data.user is None:
            raise AuthTMAError("User data is missing")
        return data.user
    except ValueError:
        raise AuthTMAError("Invalid init data")
