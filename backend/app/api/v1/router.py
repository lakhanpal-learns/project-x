from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.services import router as services_router
from app.api.v1.requests import router as requests_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.admin import router as admin_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(services_router)
router.include_router(requests_router)
router.include_router(feedback_router)
router.include_router(admin_router)
