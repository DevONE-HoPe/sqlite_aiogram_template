from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from bot.services.analytics import analytics

from bot.keyboards.inline.topics import create_categories_keyboard

router = Router(name="start")


@router.message(CommandStart())
@analytics.track_event("Sign Up")
async def start_handler(message: types.Message) -> None:
    """Welcome message."""
    start = (
        "<b>🎥 Не знаешь, что посмотреть на YouTube?</b>\n\n"
        "Просто выбери тему — я сгенерирую интересный поисковый запрос "
        "и сразу покажу тебе 5 подходящих видео.\n\n"
        "<b>👇 Выбери тему:</b>"
    )
    
    await message.answer(text=start, reply_markup=create_categories_keyboard())
    try:
        await message.delete()
    except TelegramBadRequest:
        pass