from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def build_state_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🟢 Включить" if not enabled else "🔴 Выключить",
                callback_data="toggle_assistant"
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ Текущее состояние",
                callback_data="get_status"
            )
        ]
    ])