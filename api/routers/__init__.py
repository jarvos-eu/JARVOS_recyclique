# API routers (auth, pos, reception, admin).

from .auth.router import router as auth_router
from .pos.router import router as pos_router
from .reception.router import router as reception_router
from .admin.router import router as admin_router

__all__ = ["auth_router", "pos_router", "reception_router", "admin_router"]
