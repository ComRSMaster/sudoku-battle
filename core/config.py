"""Конфигурация игры"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки, загружаемые из файла `.env`"""

    bot_token: str
    web_app_url: str
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
