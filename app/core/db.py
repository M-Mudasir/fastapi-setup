from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid

from app.models.user import crud
from app.core.config import settings
from app.models.user.model import User, UserRegister

engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True)

async def init_db(session: AsyncSession) -> None:

    result = await session.execute(

        select(User).where(User.email.ilike(settings.ADMIN_SUPERUSER))
    )
    user = result.scalars().first()
    if not user:
        user_in = UserRegister(
            id=uuid.uuid4(),
            email=settings.ADMIN_SUPERUSER.lower(),
            password=settings.ADMIN_SUPERUSER_PASSWORD,
            first_name=settings.PROJECT_NAME,
            last_name="Admin"
        )
        
        user = await crud.register_user(session=session, user_register=user_in)
        
    else:
        print("Superuser Already Exsists!")
