from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.config_aiogram import is_admin
from app.data.deep_links_loader import get_deep_links_with_names
from app.data.loader import get_welcome
from app.database.crud.user import (
    get_all_telegram_ids,
    get_all_users,
    get_users_count,
    get_users_count_by_deep_link,
)
from app.database.db_session import AsyncSessionLocal
from app.keyboards.callback_data import AdminCallbackData
from app.keyboards.main_kb import get_admin_keyboard, get_menu_keyboard
from app.states import BroadcastStates
from loguru import logger

router = Router(name="admin")


@router.callback_query(AdminCallbackData.filter(F.action == "broadcast"))
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Ask admin for broadcast text and set FSM state."""
    if callback.from_user is None:
        return
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return
    await callback.answer()
    logger.info(
        "Админ запустил рассылку: telegram_id={}, username={}",
        callback.from_user.id,
        callback.from_user.username or "—",
    )
    await state.set_state(BroadcastStates.wait_text)
    if callback.message:
        await callback.message.answer("Введите текст рассылки (одним сообщением). Отмена: /cancel")


TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def _format_users_chunks(users: list) -> list[str]:
    """Format users as text and split into chunks not exceeding Telegram limit."""
    lines: list[str] = []
    for u in users:
        username = f"@{u.username}" if u.username else "—"
        created = u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "—"
        deep = u.deep_link if u.deep_link else "—"
        lines.append(
            f"• id: {u.id}, telegram_id: {u.telegram_id}, username: {username}, дата: {created}, deep_link: {deep}"
        )
    if not lines:
        return ["Пользователей пока нет."]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in lines:
        line_len = len(line) + 1
        if current_len + line_len > TELEGRAM_MAX_MESSAGE_LENGTH and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len
    if current:
        chunks.append("\n".join(current))
    return chunks


@router.callback_query(AdminCallbackData.filter(F.action == "users_list"))
async def admin_users_list(callback: CallbackQuery) -> None:
    """Send all users from DB, split into multiple messages if over 4096 chars."""
    if callback.from_user is None or callback.message is None:
        return
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return
    await callback.answer()
    logger.info(
        "Админ запросил список пользователей: telegram_id={}, username={}",
        callback.from_user.id,
        callback.from_user.username or "—",
    )
    async with AsyncSessionLocal() as session:
        users = await get_all_users(session)
    chunks = _format_users_chunks(users)
    header = f"Список пользователей (всего {len(users)}):\n\n"
    if chunks and len(header) + len(chunks[0]) <= TELEGRAM_MAX_MESSAGE_LENGTH:
        await callback.message.answer(header + chunks[0])
        for chunk in chunks[1:]:
            await callback.message.answer(chunk)
    else:
        await callback.message.answer(header)
        for chunk in chunks:
            await callback.message.answer(chunk)


@router.callback_query(AdminCallbackData.filter())
async def admin_callback(callback: CallbackQuery, callback_data: AdminCallbackData) -> None:
    """Handle admin panel: show panel or back to main menu (broadcast handled above)."""
    if callback.from_user is None or callback.message is None:
        return
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return
    await callback.answer()
    action = callback_data.action
    logger.info(
        "Админ в панели: действие={}, telegram_id={}, username={}",
        action,
        callback.from_user.id,
        callback.from_user.username or "—",
    )
    text: str
    if action == "panel":
        async with AsyncSessionLocal() as session:
            count = await get_users_count(session)
            by_link = await get_users_count_by_deep_link(session)
        link_names = {item["slug"]: item["name"] for item in get_deep_links_with_names()}
        stats_lines = [f"Пользователей: {count}"]
        for deep_link_val, cnt in by_link:
            if deep_link_val is None:
                stats_lines.append(f"Без ссылки: {cnt}")
            else:
                name = link_names.get(deep_link_val, deep_link_val)
                stats_lines.append(f"По ссылке {deep_link_val} ({name}): {cnt}")
        text = "Админ панель.\n\n" + "\n".join(stats_lines) + "\n\nВыберите действие."
        keyboard = get_admin_keyboard()
    elif action == "back":
        welcome = get_welcome()
        text = welcome.get("text") or "Добро пожаловать! Выберите раздел в меню ниже."
        keyboard = get_menu_keyboard(None, is_admin=True)
    else:
        return
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=keyboard)
        else:
            await callback.message.edit_text(text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error("Не удалось отредактировать сообщение админки: {}", e)


@router.message(Command("cancel"), StateFilter(BroadcastStates.wait_text))
async def admin_broadcast_cancel(message: Message, state: FSMContext) -> None:
    """Cancel broadcast and clear state."""
    if message.from_user and is_admin(message.from_user.id):
        logger.info(
            "Админ отменил рассылку: telegram_id={}, username={}",
            message.from_user.id,
            message.from_user.username or "—",
        )
        await state.clear()
        await message.answer("Рассылка отменена.")


@router.message(StateFilter(BroadcastStates.wait_text))
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot) -> None:
    """Send broadcast to all users from DB. Only for admins. Error handling per user."""
    if message.from_user is None:
        return
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    text = message.text or message.caption or ""
    if not text.strip():
        await message.answer("Текст не может быть пустым. Введите текст рассылки или /cancel для отмены.")
        return
    await state.clear()
    async with AsyncSessionLocal() as session:
        user_ids = await get_all_telegram_ids(session)
    total = len(user_ids)
    logger.info(
        "Админ отправил рассылку: telegram_id={}, username={}, получателей={}",
        message.from_user.id,
        message.from_user.username or "—",
        total,
    )
    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(chat_id=uid, text=text)
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning("Рассылка не доставлена пользователю {}: {}", uid, e)
    await message.answer(
        f"Рассылка завершена. Отправлено: {sent} из {total}. Ошибок: {failed}."
    )
