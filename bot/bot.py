"""Telegram-бот игры"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from core.config import settings

dp = Dispatcher()

main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Играть в Судоку", web_app=WebAppInfo(url=settings.web_app_url)
            ),
        ]
    ]
)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Отправить пользователю кнопку запуска Web App"""
    await message.answer(
        "Привет, это бот Sudoku Battle! Нажимай на кнопку ниже, чтобы запустить игру:",
        reply_markup=main_menu_keyboard,
    )


async def run_bot() -> None:
    """Запустить polling Telegram-бота"""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # TODO: заменить pooling на webhook
    await dp.start_polling(bot)
