"""API Routers."""
from backend.app.routers.auth import router as auth_router
from backend.app.routers.users import router as users_router
from backend.app.routers.media import router as media_router
from backend.app.routers.video import router as video_router
from backend.app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router", 
    "media_router",
    "video_router",
    "admin_router",
]
