from aiogram.filters.callback_data import CallbackData


class MenuCallbackData(CallbackData, prefix="menu"):
    """Callback data for menu navigation: open section or go back."""

    action: str  # "open" | "back"
    path: str  # "" for main menu, "1", "1_2", "2_4", etc.


class AdminCallbackData(CallbackData, prefix="admin"):
    """Callback data for admin panel: panel, broadcast, users_list, back."""

    action: str  # "panel" | "broadcast" | "users_list" | "back"
