"""Настройка loguru: вывод в консоль и в файлы в app/logs."""
import sys
from pathlib import Path

from loguru import logger

# Каталог логов относительно корня приложения (папка app)
APP_LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"

# Формат с уровнем и временем
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>"
FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}"


def setup_logging() -> None:
    """Настроить loguru: убрать вывод по умолчанию, добавить консоль и файл в app/logs."""
    logger.remove()
    APP_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = APP_LOGS_DIR / "bot_{time:YYYY-MM-DD}.log"
    logger.add(
        log_file,
        format=FILE_FORMAT,
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        encoding="utf-8",
    )
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level="INFO",
        colorize=True,
    )
