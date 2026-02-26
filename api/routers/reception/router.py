"""Router réception — stub pour Story 1.2."""

from fastapi import APIRouter

router = APIRouter(tags=["reception"])


@router.get("/")
def reception_root() -> dict:
    """Stub : module reception monté sous /api/reception."""
    return {"module": "reception"}
