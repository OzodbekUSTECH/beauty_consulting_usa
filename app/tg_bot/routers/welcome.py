from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/assistant")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await message.answer(
        "👋 Привет! Я бот для управления Beauty Consulting USA Assistant.\n"
        "Чтобы узнать текущее состояние ассистента или изменить его, нажми /assistant.\n\n"
        "🔍 <b>Как найти пользователя:</b>\n"
        "• Перешли мне сообщение пользователя\n"
        "• Напиши ID пользователя (можно узнать через @getidsbot)\n"
        "• Напиши имя пользователя как указано в Telegram\n"
        "• Введи номер телефона (начиная с +)\n"
        "• Напиши @username пользователя",
        parse_mode="HTML",
        reply_markup=keyboard
    )
