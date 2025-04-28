from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import engine
from app.core.config import settings
from app.models.user.crud import authenticate
from app.models.user.model import User

class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key=secret_key)

    async def login(self, request: Request, session: AsyncSession = None) -> bool:
        if session is None:
            async with AsyncSession(engine) as session:
                return await self._perform_login(request, session)
        else:
            return await self._perform_login(request, session)

    async def _perform_login(self, request: Request, session: AsyncSession) -> bool:
        form = await request.form()
        email = form.get("username").lower()
        password = form.get("password")

        user = await authenticate(
            session=session, email=email, password=password
        )

        if user:
            request.session.update({"token": user.email})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token is not None

class UsersAdmin(ModelView, model=User):
    column_list = [
        'id', 'email', 'name', 'status'
    ]

def create_admin(app):
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(UsersAdmin)
    return admin
