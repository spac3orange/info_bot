from pathlib import Path
from typing import Any

import yaml
from loguru import logger

_content: dict[str, Any] | None = None

DEFAULT_SECTIONS_PATH = Path(__file__).resolve().parent / "sections.yaml"


def load_sections(file_path: str | Path | None = None) -> dict[str, Any]:
    """Load sections and welcome data from YAML. Cached in memory."""
    global _content
    path = Path(file_path) if file_path else DEFAULT_SECTIONS_PATH
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    if not path.exists():
        raise FileNotFoundError(f"Sections file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        _content = yaml.safe_load(f)
    if not _content or "sections" not in _content:
        raise ValueError("sections.yaml must contain 'sections' key")
    logger.info("Разделы загружены из {}", path)
    return _content


def get_content() -> dict[str, Any]:
    """Return cached content; load from file if not yet loaded."""
    global _content
    if _content is None:
        load_sections()
    return _content


def _find_node_by_path(nodes: list[dict], path: str) -> dict[str, Any] | None:
    """Find a node in nested list by path like '1' or '1_2'."""
    parts = path.split("_") if path else []
    if not parts:
        return None
    current = nodes
    for i, part in enumerate(parts):
        key = "_".join(parts[: i + 1])
        found = None
        for node in current:
            if node.get("id") == key:
                found = node
                break
        if found is None:
            return None
        if i == len(parts) - 1:
            return found
        current = found.get("children") or []
    return None


def get_children_for_path(path: str | None) -> list[dict[str, Any]]:
    """Return list of child nodes for the given path. path '' or None = top-level sections."""
    content = get_content()
    sections = content.get("sections") or []
    if not path or path == "":
        return sections
    node = _find_node_by_path(sections, path)
    if node is None:
        return []
    return node.get("children") or []


def get_text_for_path(path: str | None) -> str:
    """Return message text for the given path. path '' or None = welcome text."""
    content = get_content()
    if not path or path == "":
        welcome = content.get("welcome") or {}
        return welcome.get("text") or "Добро пожаловать! Выберите раздел в меню ниже."
    sections = content.get("sections") or []
    node = _find_node_by_path(sections, path)
    if node is None:
        return ""
    return node.get("text") or ""


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _is_url(s: str) -> bool:
    return (s or "").strip().lower().startswith(("http://", "https://"))


def _resolve_image(item: str) -> str:
    """Return URL as-is; resolve file path relative to project root."""
    item = (item or "").strip()
    if not item:
        return ""
    if _is_url(item):
        return item
    path = Path(item)
    if not path.is_absolute():
        path = _PROJECT_ROOT / path
    return str(path.resolve())


def get_images_for_path(path: str | None) -> list[str]:
    """Return up to 3 image sources (URL or file path) for the section. Empty list if none."""
    content = get_content()
    if not path or path == "":
        welcome = content.get("welcome") or {}
        out: list[str] = []
        for key in ("image_url", "image_path"):
            v = welcome.get(key)
            if v and str(v).strip():
                out.append(_resolve_image(str(v)))
        return out[:3]
    sections = content.get("sections") or []
    node = _find_node_by_path(sections, path)
    if node is None:
        return []
    raw = node.get("images") or []
    if not isinstance(raw, list):
        return []
    resolved = [_resolve_image(str(x)) for x in raw[:3] if x]
    return [r for r in resolved if r]


def get_parent_path(path: str) -> str:
    """Return parent path. E.g. '1_2' -> '1', '1' -> ''."""
    if not path or path == "":
        return ""
    parts = path.split("_")
    if len(parts) <= 1:
        return ""
    return "_".join(parts[:-1])


def get_welcome() -> dict[str, Any]:
    """Return welcome config (text, image_path, image_url)."""
    content = get_content()
    return content.get("welcome") or {}


def get_info_text() -> str:
    """Return text for /info (О нас) page. Editable via sections.yaml."""
    content = get_content()
    info_block = content.get("info") or {}
    return info_block.get("text") or "О нас. Здесь можно разместить информацию о проекте или организации."


def get_info_images() -> list[str]:
    """Return up to 3 image sources (URL or file path) for /info. Empty list if none."""
    content = get_content()
    info_block = content.get("info") or {}
    raw = info_block.get("images") or []
    if not isinstance(raw, list):
        return []
    resolved = [_resolve_image(str(x)) for x in raw[:3] if x]
    return [r for r in resolved if r]
