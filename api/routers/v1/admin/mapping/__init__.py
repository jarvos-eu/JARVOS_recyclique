# Router admin mapping (Story 7.2). Prefixe /v1/admin/mapping.
# Reutilisation modele et services 7-1 ; RBAC admin ou responsable compta ; audit sur create/update/delete.

from fastapi import APIRouter

from api.routers.v1.admin.mapping.payment_methods import router as payment_methods_router
from api.routers.v1.admin.mapping.categories import router as categories_router
from api.routers.v1.admin.mapping.locations import router as locations_router

router = APIRouter()
router.include_router(payment_methods_router)
router.include_router(categories_router)
router.include_router(locations_router)
