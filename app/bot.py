import asyncio
from pathlib import Path

from aiogram import Dispatcher
from aiogram.types import BotCommand
from loguru import logger

from app.core.config_aiogram import aiogram_bot
from app.core.logging_config import setup_logging
from app.data.deep_links_loader import load_deep_links
from app.data.loader import load_sections
from app.database import init_db
from app.handlers import router


async def set_commands() -> None:
    """Set context menu (pop-up) commands: /start — Главное меню, /info — О нас."""
    await aiogram_bot.set_my_commands(
        [
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="info", description="О нас"),
        ]
    )


async def main() -> None:
    setup_logging()
    Path("data").mkdir(exist_ok=True)
    load_sections()
    load_deep_links()
    await init_db()
    await set_commands()
    dp = Dispatcher()
    dp.include_router(router)
    logger.info("Бот запускает long polling")
    await dp.start_polling(aiogram_bot)


if __name__ == "__main__":
    asyncio.run(main())
