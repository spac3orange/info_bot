from pathlib import Path

from environs import Env
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


class TgBot:
    def __init__(self, token: str):
        self.token = token


class Config:
    def __init__(self, tg_bot: TgBot, admin_id: str):
        self.tg_bot = tg_bot
        self.admin_ids = [x.strip() for x in admin_id.split(",") if x.strip()]


def load_config(path: str | Path | None = None) -> Config:
    env = Env()
    if path is None:
        path = Path(__file__).resolve().parent.parent / ".env"
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')), admin_id=env('ADMIN_ID'))


config_aiogram = load_config()


def is_admin(telegram_id: int) -> bool:
    """Return True if telegram_id is in ADMIN_ID from env."""
    return str(telegram_id) in config_aiogram.admin_ids


aiogram_bot = Bot(token=config_aiogram.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
