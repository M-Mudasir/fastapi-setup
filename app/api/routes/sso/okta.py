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

router = APIRouter(prefix="/okta")

@router.get("/login")
async def okta_login(request: Request):
    next_url = request.query_params.get("next", settings.FRONTEND_URL)

    authorization_url = f"https://{settings.OKTA_BASE_URL}/oauth2/v1/authorize"

    state_data = {"next": next_url}
    state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()

    redirect_uri = (
        f"{authorization_url}?client_id={settings.OKTA_AUTH_CLIENT_ID}"
        f"&response_type=code&scope=openid%20email%20profile"
        f"&redirect_uri={settings.SERVER_URL}/api/sso/okta/callback&state={state}"
    )
    return RedirectResponse(url=redirect_uri)


@router.get("/callback")
async def okta_callback(session: SessionDep, code: str, state: str):
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
        next_url = state_data.get("next")
        separator = "&" if "?" in next_url else "?" 
    except (json.JSONDecodeError, KeyError):
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    try:
        token_url = f"https://{settings.OKTA_BASE_URL}/oauth2/v1/token"
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": f"{settings.SERVER_URL}/api/sso/okta/callback",
                    "client_id": settings.OKTA_AUTH_CLIENT_ID,
                    "client_secret": settings.OKTA_AUTH_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_response.raise_for_status()
            token_data = token_response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")

        user_profile_url = f"https://{settings.OKTA_BASE_URL}/oauth2/v1/userinfo"
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
            raise HTTPException(status_code=400, detail="Email attribute is missing in the Okta response")

        user = await get_or_create_user(session=session, user_register=UserRegister(email=email, first_name=first_name, last_name=last_name, password=password))

        response = RedirectResponse(url=f"{next_url}{separator}token={security.create_access_token(user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))}")

        return response

    except Exception as e:
        logging.error("Error in handling Okta SSO", exc_info=e)
        return RedirectResponse(url=settings.FRONTEND_URL)
