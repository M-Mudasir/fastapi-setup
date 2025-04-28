from datetime import timedelta
import logging
import json
import base64
import secrets
import httpx

from fastapi import HTTPException, Request, APIRouter
from fastapi.responses import RedirectResponse

from app.models.user.crud import get_or_create_user
from app.models.user.model import UserRegister
from app.core import security
from app.core.config import settings
from app.api.deps import SessionDep


router = APIRouter(prefix="/linkedin")

@router.get("/login")
async def linkedin_login(request: Request, next: str | None = None):
    next_url = next or settings.FRONTEND_URL

    state_data = {"next": next_url}
    state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()

    redirect_uri = (f"https://www.linkedin.com/oauth/v2/authorization?"
                    f"response_type=code&client_id={settings.LINKEDIN_AUTH_CLIENT_ID}&redirect_uri="
                    f"{settings.SERVER_URL}/api/sso/linkedin/callback&state={state}&scope=openid+profile+email")

    return RedirectResponse(url=redirect_uri)


@router.get("/callback")
async def linkedin_callback(session: SessionDep, code: str, state: str):
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
        next_url = state_data.get("next")
        separator = "&" if "?" in next_url else "?" 
    except (json.JSONDecodeError, KeyError):
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    try:
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": f"{settings.SERVER_URL}/api/sso/linkedin/callback",
                    "client_id": settings.LINKEDIN_AUTH_CLIENT_ID,
                    "client_secret": settings.LINKEDIN_AUTH_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_response.raise_for_status()
            token_data = token_response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")

        user_profile_url = "https://api.linkedin.com/v2/userinfo"
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(
                user_profile_url, headers={"Authorization": f"Bearer {access_token}"}
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()

        email = profile_data.get("email")
        first_name = profile_data.get("given_name", "").strip()
        last_name = profile_data.get("family_name", "").strip()
        password=secrets.token_urlsafe(16)

        if not email:
            raise HTTPException(status_code=400, detail="Email attribute is missing in the LinkedIn response")

        user = await get_or_create_user(session=session, user_register=UserRegister(email=email, first_name=first_name, last_name=last_name, password=password))
        response = RedirectResponse(url=f"{next_url}{separator}token={security.create_access_token(user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))}")

        return response

    except Exception as e:
        logging.error("Error in handling LinkedIn SSO", exc_info=e)
        return RedirectResponse(url=settings.FRONTEND_URL)
