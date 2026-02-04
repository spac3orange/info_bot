from aiogram import Router

from app.handlers.admin import router as admin_router
from app.handlers.menu import router as menu_router
from app.handlers.start import router as start_router

router = Router(name="root")
router.include_router(start_router)
router.include_router(admin_router)
router.include_router(menu_router)
