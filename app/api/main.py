from fastapi import APIRouter

from app.api.routes.utils import utils
from app.api.routes.login import login
from app.api.routes.user import user
from app.api.routes.sso import main

api_router = APIRouter()

api_router.include_router(utils.router)
api_router.include_router(login.router)
api_router.include_router(user.router)
api_router.include_router(main.router)