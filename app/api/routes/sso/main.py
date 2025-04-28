from fastapi import APIRouter

from .okta import router as okta_router
from .google import router as google_router
from .linkedin import router as linkedin_router
from .microsoft import router as microsoft_router

router = APIRouter(prefix="/sso", tags=["sso"])

router.include_router(okta_router)
router.include_router(google_router)
router.include_router(linkedin_router)
router.include_router(microsoft_router)