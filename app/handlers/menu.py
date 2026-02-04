from aiogram import Bot, Router
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto

from app.core.config_aiogram import is_admin
from app.data.loader import get_images_for_path, get_text_for_path
from app.keyboards.callback_data import MenuCallbackData
from app.keyboards.main_kb import get_menu_keyboard
from loguru import logger

router = Router(name="menu")

# Сообщения медиа-группы (2–3 картинки) по chat_id — удаляем при смене раздела
_media_group_ids: dict[int, list[int]] = {}


def _photo_media(source: str):
    """URL — строка, иначе FSInputFile по пути."""
    if (source or "").strip().lower().startswith(("http://", "https://")):
        return source
    return FSInputFile(source)


async def _delete_media_group(bot: Bot, chat_id: int) -> None:
    """Удалить ранее отправленную медиа-группу, если есть."""
    ids = _media_group_ids.pop(chat_id, None)
    if not ids:
        return
    try:
        for mid in ids:
            await bot.delete_message(chat_id=chat_id, message_id=mid)
    except Exception as e:
        logger.debug("Не удалось удалить сообщения медиа-группы: {}", e)


@router.callback_query(MenuCallbackData.filter())
async def menu_callback(
    callback: CallbackQuery,
    callback_data: MenuCallbackData,
    bot: Bot,
) -> None:
    """Показать раздел: текст, до 3 картинок (0/1 или 2–3), клавиатура."""
    await callback.answer()
    path = callback_data.path
    from_user = callback.from_user
    if from_user:
        logger.info(
            "Пользователь в меню: действие={}, путь={}, telegram_id={}, username={}",
            callback_data.action,
            path or "главное",
            from_user.id,
            from_user.username or "—",
        )
    text = get_text_for_path(path)
    images = get_images_for_path(path)
    user_id = callback.from_user.id if callback.from_user else 0
    keyboard = get_menu_keyboard(path, is_admin=is_admin(user_id))
    if callback.message is None:
        return
    chat_id = callback.message.chat.id
    msg = callback.message
    had_photo = bool(msg.photo)

    try:
        await _delete_media_group(bot, chat_id)
    except Exception as e:
        logger.debug("Удаление медиа-группы: {}", e)

    try:
        if len(images) == 0:
            if had_photo:
                await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=keyboard,
                )
            else:
                await msg.edit_text(text=text, reply_markup=keyboard)

        elif len(images) == 1:
            media = _photo_media(images[0])
            if had_photo:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=msg.message_id,
                    media=InputMediaPhoto(media=media, caption=text),
                    reply_markup=keyboard,
                )
            else:
                await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=media,
                    caption=text,
                    reply_markup=keyboard,
                )

        else:
            # 2 или 3 картинки: медиа-группа + отдельное сообщение с текстом и клавиатурой
            media_list = [
                InputMediaPhoto(media=_photo_media(src)) for src in images
            ]
            sent = await bot.send_media_group(chat_id=chat_id, media=media_list)
            _media_group_ids[chat_id] = [m.message_id for m in sent]
            if had_photo:
                await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=keyboard,
                )
            else:
                await msg.edit_text(text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error("Не удалось обновить сообщение меню: {}", e)
