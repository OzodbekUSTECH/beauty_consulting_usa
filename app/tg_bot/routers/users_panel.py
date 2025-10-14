from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import FromDishka
from app.dto.users import GetUsersParams, UpdateUserRequest
from app.interactors.users.update import UpdateUserInteractor
from app.tg_bot.buttons.inline.user_state import build_user_state_keyboard
from app.tg_bot.schemes.users import UserResponse
from app.interactors.users.get import GetAllUsersInteractor, GetUserByTgIdInteractor

router = Router()


@router.message()
async def get_user_menu(
    message: Message, 
    get_all_users_interactor: FromDishka[GetAllUsersInteractor]
):
    # Проверяем, пересланное ли это сообщение
    if message.forward_from:
        # Если мы можем получить полную информацию о переславшем
        tg_id = str(message.forward_from.id)
        search_type = "ID пересланного сообщения"
        search_value = tg_id
        users = await get_all_users_interactor.execute(GetUsersParams(filter_by="tg_id", filter=tg_id))

    elif message.forward_sender_name:
        # Если пользователь скрыл свои данные, у нас будет только имя
        search_type = "имени пересланного сообщения (Данные скрыты)"
        search_value = message.forward_sender_name
        users = await get_all_users_interactor.execute(GetUsersParams(filter_by="name", filter=message.forward_sender_name))

    else:
        # Это не пересланное сообщение, обрабатываем как текстовый ввод
        input_text = message.text.strip()

        # Проверяем формат ввода
        if input_text.startswith("+") and input_text[1:].isdigit():
            # Номер телефона
            search_type = "номеру телефона"
            search_value = input_text
            users = await get_all_users_interactor.execute(GetUsersParams(filter_by="phone_number", filter=input_text[1:]))

        elif input_text.startswith("@"):
            # Имя пользователя
            search_type = "имени пользователя"
            search_value = input_text
            username = input_text[1:]  # Убираем @ для поиска
            users = await get_all_users_interactor.execute(GetUsersParams(filter_by="username", filter=username))

        elif input_text.isdigit():
            # Поиск по ID
            search_type = "ID"
            search_value = input_text
            user_id = str(int(input_text))
            users = await get_all_users_interactor.execute(GetUsersParams(filter_by="tg_id", filter=user_id))

        else:
            # Если это имя, например "Елена В"
            search_type = "имени"
            search_value = input_text
            users = await get_all_users_interactor.execute(GetUsersParams(filter_by="name", filter=input_text))

    # Проверяем, нашли ли пользователей
    if not users or len(users) == 0:
        await message.answer(
            f"🔍 <b>Пользователи не найдены</b>\n\n"
            f"Поиск по {search_type}: <code>{search_value}</code>\n\n"
            f"Пожалуйста, проверьте введенные данные и попробуйте снова.\n\n"
            f"ℹ️ <b>Как найти пользователя:</b>\n"
            f"• Перешли сообщение пользователя\n"
            f"• Напиши ID пользователя (можно узнать через @getidsbot)\n"
            f"• Напиши имя пользователя как указано в Telegram\n"
            f"• Введи номер телефона (начиная с +)\n"
            f"• Напиши @username пользователя",
            parse_mode="HTML"
        )
        return

    # Выводим количество найденных пользователей
    result_header = (
        f"🔍 <b>Результаты поиска</b>\n\n"
        f"Найдено пользователей: <b>{len(users)}</b>\n"
        f"Поиск по {search_type}: <code>{search_value}</code>\n"
    )
    await message.answer(result_header, parse_mode="HTML")

    # Для каждого пользователя создаем сообщение с кнопкой
    for user in users:
        tg_id = user.tg_id
        state = user.is_active
        status_emoji = "🟢" if state else "🔴"
        status_text = "ВКЛЮЧЕН" if state else "ВЫКЛЮЧЕН"

        user_info = format_user_info(user, status_emoji, status_text)
        await message.answer(user_info, reply_markup=build_user_state_keyboard(tg_id, state), parse_mode="HTML")


# Вспомогательная функция для форматирования информации о пользователе
def format_user_info(user: UserResponse, status_emoji, status_text):
    user_info = (
        f"👤 <b>Пользователь</b> {status_emoji}\n\n"
        f"<b>ID:</b> <code>{user.tg_id}</code>\n"
        f"<b>Статус:</b> {status_emoji} {status_text}\n"
    )

    # Дополнительная информация о пользователе, если доступна
    if hasattr(user, 'username') and user.username:
        user_info += f"<b>Username:</b> @{user.username}\n"
    if hasattr(user, 'phone_number') and user.phone_number:
        formatted_phone = user.phone_number
        if not formatted_phone.startswith("+"):
            formatted_phone = f"+{formatted_phone}"
        user_info += f"<b>Телефон:</b> <code>{formatted_phone}</code>\n"
    if hasattr(user, 'name') and user.name:
        user_info += f"<b>Имя:</b> {user.name}\n"

    return user_info


@router.callback_query(F.data.startswith("toggle_user:"))
async def toggle_user(
    call: CallbackQuery, 
    update_user_interactor: FromDishka[UpdateUserInteractor],
    get_user_by_tg_id_interactor: FromDishka[GetUserByTgIdInteractor]
):
    await call.answer("⏳ Ожидайте...", show_alert=False)

    tg_id = call.data.split(":")[1]  # Extract tg_id from callback data
    user = await get_user_by_tg_id_interactor.execute(tg_id)

    if user is None:
        await call.answer("Пользователь не найден.", show_alert=True)
        return

    new_state = not user.is_active  # Toggle user state
    updated_user = await update_user_interactor.execute(UpdateUserRequest(tg_id=tg_id, is_active=new_state))  # Pass tg_id to update state

    status_emoji = "🟢" if new_state else "🔴"
    status_text = "ВКЛЮЧЕН" if new_state else "ВЫКЛЮЧЕН"

    # Используем ту же функцию форматирования
    user_info = format_user_info(updated_user, status_emoji, status_text)

    await call.message.edit_text(
        user_info,
        reply_markup=build_user_state_keyboard(tg_id, new_state),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("get_user_status:"))
async def get_user_status(
    call: CallbackQuery, 
    get_user_by_tg_id_interactor: FromDishka[GetUserByTgIdInteractor]
):
    tg_id = call.data.split(":")[1]  # Extract tg_id from callback data
    user = await get_user_by_tg_id_interactor.execute(tg_id)

    if user is None:
        await call.answer("Пользователь не найден.", show_alert=True)
        return

    state = user.is_active
    status_emoji = "🟢" if state else "🔴"
    status_text = "ВКЛЮЧЕН" if state else "ВЫКЛЮЧЕН"

    await call.answer(
        f"Статус пользователя (ID: {tg_id}): {status_emoji} {status_text}",
        show_alert=True
    )