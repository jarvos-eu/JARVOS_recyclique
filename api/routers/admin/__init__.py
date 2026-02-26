# Admin routers. Health est monté à la racine de l'app dans main.py (GET /health).

from .router import router as admin_router

__all__ = ["admin_router"]
