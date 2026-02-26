"""Router pos — stub pour Story 1.2."""

from fastapi import APIRouter

router = APIRouter(tags=["pos"])


@router.get("/")
def pos_root() -> dict:
    """Stub : module pos monté sous /api/pos."""
    return {"module": "pos"}
