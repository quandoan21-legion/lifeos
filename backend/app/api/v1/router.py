from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.events import router as events_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(events_router)


@router.get("/health")
async def health_check():
    return {"status": "ok"}
