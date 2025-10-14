from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import FromDishka

from app.tg_bot.buttons.inline.assistant_state import build_state_keyboard
from app.utils.ai_state import AIAssistantStateService

router = Router()


@router.message(F.text.lower() == "/assistant")
async def assistant_menu(message: Message, assistant_state: FromDishka[AIAssistantStateService]):
    state = await assistant_state.get_state()
    text = f"🤖 Состояние ассистента: {'🟢 ВКЛЮЧЕН' if state else '🔴 ВЫКЛЮЧЕН'}"
    await message.answer(text, reply_markup=build_state_keyboard(state))

@router.callback_query(F.data == "toggle_assistant")
async def toggle_assistant(call: CallbackQuery, assistant_state: FromDishka[AIAssistantStateService]):
    # 1. Отвечаем сразу, чтобы пользователь видел реакцию
    await call.answer("⏳ Ожидайте...", show_alert=False)

    # 2. Выполняем сам запрос
    new_state = await assistant_state.toggle_state()
    new_text = f"✅ Ассистент теперь: {'🟢 ВКЛЮЧЕН' if new_state else '🔴 ВЫКЛЮЧЕН'}"

    # 3. Обновляем сообщение
    await call.message.edit_text(new_text, reply_markup=build_state_keyboard(new_state))

@router.callback_query(F.data == "get_status")
async def get_status(call: CallbackQuery, assistant_state: FromDishka[AIAssistantStateService]):
    state = await assistant_state.get_state()
    await call.answer(f"Ассистент сейчас: {'ВКЛЮЧЕН 🟢' if state else 'ВЫКЛЮЧЕН 🔴'}", show_alert=True)
