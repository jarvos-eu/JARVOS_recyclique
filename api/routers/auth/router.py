"""Router auth — stub pour Story 1.2."""

from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@router.get("/")
def auth_root() -> dict:
    """Stub : module auth monté sous /api/auth."""
    return {"module": "auth"}
