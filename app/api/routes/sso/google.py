from datetime import timedelta
import logging
import secrets

from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO

from app.models.user.crud import get_or_create_user
from app.models.user.model import UserRegister
from app.core import security
from app.core.config import settings
from app.api.deps import SessionDep

router = APIRouter(prefix="/google")

google_sso = GoogleSSO(settings.GOOGLE_AUTH_CLIENT_ID, 
                       settings.GOOGLE_AUTH_CLIENT_SECRET, 
                       f"{settings.SERVER_URL}/api/sso/google/callback")

@router.get("/login")
async def google_login(next: str | None = None):
    next_url = next or settings.FRONTEND_URL
    
    async with google_sso:
        return await google_sso.get_login_redirect(state=next_url)


@router.get("/callback")
async def google_callback(request: Request, session: SessionDep):
    try:

        next_url = request.query_params.get("state")
        separator = "&" if "?" in next_url else "?"
            
        async with google_sso:
            user = await google_sso.verify_and_process(request)
            profile_data = user.model_dump()

        email = profile_data.get("email")
        first_name = (profile_data.get("first_name") or "").strip()
        last_name = (profile_data.get("last_name") or "").strip()
        password=secrets.token_urlsafe(16)

        if not email:
            raise HTTPException(status_code=400, detail="Email attribute is missing in the Microsoft response")

        user = await get_or_create_user(session=session, user_register=UserRegister(email=email, first_name=first_name, last_name=last_name, password=password))

        response = RedirectResponse(url=f"{next_url}{separator}token={security.create_access_token(user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))}")

        return response
    except Exception as e:
        logging.error("Error in handling Google SSO", exc_info=e)
        return RedirectResponse(url=settings.FRONTEND_URL)