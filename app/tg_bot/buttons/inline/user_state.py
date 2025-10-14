from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def build_user_state_keyboard(tg_id: str, is_active: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🟢 Включить" if not is_active else "🔴 Выключить",
                callback_data=f"toggle_user:{tg_id}"  # include tg_id in callback data
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ Текущее состояние",
                callback_data=f"get_user_status:{tg_id}"  # include tg_id in callback data
            )
        ]
    ])