from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(
            text="Кнопка",
            callback_data="start_keyboard"
        )
    )
    return keyboard_builder.as_markup()