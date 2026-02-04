from pathlib import Path
from typing import Any

import yaml
from loguru import logger

_deep_links_data: list[dict[str, Any]] | None = None

DEFAULT_DEEP_LINKS_PATH = Path(__file__).resolve().parent / "deep_links.yaml"


def load_deep_links(file_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load deep links config from YAML. Cached in memory."""
    global _deep_links_data
    path = Path(file_path) if file_path else DEFAULT_DEEP_LINKS_PATH
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    if not path.exists():
        logger.warning("Файл deep links не найден: {}, используется пустой список", path)
        _deep_links_data = []
        return _deep_links_data
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    raw = (data or {}).get("links")
    if not isinstance(raw, list):
        _deep_links_data = []
        return _deep_links_data
    _deep_links_data = []
    for item in raw:
        if isinstance(item, dict) and item.get("slug"):
            _deep_links_data.append({
                "slug": str(item["slug"]).strip(),
                "name": str(item.get("name") or item["slug"]).strip(),
            })
        elif isinstance(item, str) and item.strip():
            s = item.strip()
            _deep_links_data.append({"slug": s, "name": s})
    logger.info("Deep links загружены из {}: {} ссылок", path, len(_deep_links_data))
    return _deep_links_data


def get_valid_deep_link_slugs() -> list[str]:
    """Return list of valid slug strings (for validation). Load from file if not cached."""
    if _deep_links_data is None:
        load_deep_links()
    return [item["slug"] for item in (_deep_links_data or [])]


def get_deep_links_with_names() -> list[dict[str, str]]:
    """Return list of {slug, name} for admin stats. Load from file if not cached."""
    if _deep_links_data is None:
        load_deep_links()
    return list(_deep_links_data or [])
