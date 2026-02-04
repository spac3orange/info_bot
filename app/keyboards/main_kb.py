from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.data.loader import get_children_for_path, get_parent_path
from app.keyboards.callback_data import AdminCallbackData, MenuCallbackData


def get_menu_keyboard(path: str | None, is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for the given path.
    path None or '' = main menu (5 sections + optional Admin panel); otherwise children + Back button.
    """
    path = path or ""
    builder = InlineKeyboardBuilder()
    children = get_children_for_path(path)

    for node in children:
        node_id = node.get("id", "")
        title = node.get("title", node_id)
        builder.button(
            text=title,
            callback_data=MenuCallbackData(action="open", path=node_id),
        )

    if path == "" and is_admin:
        builder.button(
            text="Админ панель",
            callback_data=AdminCallbackData(action="panel"),
        )

    parent_path = get_parent_path(path)
    if path != "":
        builder.button(
            text="Назад",
            callback_data=MenuCallbackData(action="back", path=parent_path),
        )

    builder.adjust(1)
    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel: Рассылка, Список пользователей, Назад to main menu."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Рассылка",
        callback_data=AdminCallbackData(action="broadcast"),
    )
    builder.button(
        text="Список пользователей",
        callback_data=AdminCallbackData(action="users_list"),
    )
    builder.button(
        text="Назад",
        callback_data=AdminCallbackData(action="back"),
    )
    builder.adjust(1)
    return builder.as_markup()
