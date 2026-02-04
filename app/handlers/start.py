from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, InputMediaPhoto, Message

from loguru import logger

from app.core.config_aiogram import is_admin
from app.data.deep_links_loader import get_valid_deep_link_slugs
from app.data.loader import get_info_images, get_info_text, get_welcome
from app.database.crud.user import get_or_create_user
from app.database.db_session import AsyncSessionLocal
from app.keyboards.main_kb import get_menu_keyboard

router = Router(name="start")


def _parse_start_payload(text: str | None) -> str | None:
    """Extract deep link payload from /start command. Returns None if no payload or invalid."""
    if not text:
        return None
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return None
    payload = parts[1].strip()
    if not payload:
        return None
    valid = get_valid_deep_link_slugs()
    return payload if payload in valid else None


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Save user to DB (with deep_link if came via valid deep link), send welcome and main menu."""
    user = message.from_user
    if user is None:
        return
    deep_link = _parse_start_payload(message.text)
    logger.info(
        "Пользователь запустил бота: telegram_id={}, username={}, deep_link={}",
        user.id,
        user.username or "—",
        deep_link or "—",
    )
    async with AsyncSessionLocal() as session:
        await get_or_create_user(
            session,
            telegram_id=user.id,
            username=user.username,
            deep_link=deep_link,
        )
    welcome = get_welcome()
    text = welcome.get("text") or "Добро пожаловать! Выберите раздел в меню ниже."
    image_path = welcome.get("image_path") or ""
    image_url = welcome.get("image_url") or ""
    admin = is_admin(user.id)
    keyboard = get_menu_keyboard(None, is_admin=admin)

    if image_path:
        try:
            photo = FSInputFile(image_path)
            await message.answer_photo(photo=photo, caption=text, reply_markup=keyboard)
        except Exception:
            await message.answer(text=text, reply_markup=keyboard)
    elif image_url:
        await message.answer_photo(photo=image_url, caption=text, reply_markup=keyboard)
    else:
        await message.answer(text=text, reply_markup=keyboard)


def _photo_media(source: str):
    """URL — строка, иначе FSInputFile по пути."""
    if (source or "").strip().lower().startswith(("http://", "https://")):
        return source
    return FSInputFile(source)


@router.message(Command("info"))
async def cmd_info(message: Message, bot: Bot) -> None:
    """Show О нас text and optional images from sections.yaml, main menu keyboard."""
    user = message.from_user
    if user:
        logger.info(
            "Пользователь открыл «О нас»: telegram_id={}, username={}",
            user.id,
            user.username or "—",
        )
    admin = is_admin(user.id) if user else False
    text = get_info_text()
    images = get_info_images()
    keyboard = get_menu_keyboard(None, is_admin=admin)

    if len(images) == 0:
        await message.answer(text=text)
    elif len(images) == 1:
        media = _photo_media(images[0])
        await message.answer_photo(
            photo=media,
            caption=text
        )
    else:
        media_list = [InputMediaPhoto(media=_photo_media(src)) for src in images]
        await bot.send_media_group(chat_id=message.chat.id, media=media_list)
        await message.answer(text=text)
