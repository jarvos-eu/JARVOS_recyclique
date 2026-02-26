# RecyClique API — FastAPI app (socle Epic 1 + sites Story 2.1).

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from api.core.modules.loader import load_modules_from_toml
from api.routers import auth_router, pos_router, reception_router, admin_router
from api.routers.admin.health import router as health_router
from api.routers.sites import router as sites_router
from api.routers.cash_registers import router as cash_registers_router
from api.routers.categories import router as categories_router
from api.routers.presets import router as presets_router

app = FastAPI(title="RecyClique API")

# Chargement des modules (TOML, ModuleBase) — Story 1.4
load_modules_from_toml(app)

# Health à la racine (GET /health)
app.include_router(health_router)

# Routers métier sous /api
app.include_router(auth_router, prefix="/api/auth")
app.include_router(pos_router, prefix="/api/pos")
app.include_router(reception_router, prefix="/api/reception")
app.include_router(admin_router, prefix="/api/admin")

# API v1 : sites CRUD (GET/POST/PATCH/DELETE /v1/sites)
app.include_router(sites_router, prefix="/v1")
# API v1 : postes de caisse CRUD + GET /status (Story 2.2)
app.include_router(cash_registers_router, prefix="/v1")
# API v1 : categories CRUD, hierarchy, visibilité, ordre, soft delete (Story 2.3)
app.include_router(categories_router, prefix="/v1")
# API v1 : presets CRUD + GET /active (Story 2.4)
app.include_router(presets_router, prefix="/v1")

# Statics SPA (frontend/dist)
dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist.exists() and (dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def catch_all_spa(full_path: str):
        """Catch-all pour SPA : renvoie index.html."""
        if full_path and not full_path.startswith(("api/", "v1/", "health", "docs", "openapi", "assets")):
            return FileResponse(dist / "index.html")
        return JSONResponse({"detail": "Not Found", "message": "Path not found"}, status_code=404)
else:
    @app.get("/{full_path:path}")
    def catch_all_no_dist(full_path: str):
        """Build frontend absent : JSON explicite."""
        return JSONResponse(
            {"message": "Frontend build not found", "detail": "Run npm run build in frontend/"},
            status_code=200,
        )
