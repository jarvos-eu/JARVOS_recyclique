# Router mapping RecyClique -> Paheko (Story 7.1). Préfixe /api/mapping.

from fastapi import APIRouter

from api.routers.mapping.categories import router as categories_router
from api.routers.mapping.locations import router as locations_router
from api.routers.mapping.payment_methods import router as payment_methods_router

router = APIRouter()
router.include_router(payment_methods_router)
router.include_router(categories_router)
router.include_router(locations_router)
