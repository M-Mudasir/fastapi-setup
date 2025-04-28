from typing import Any, Optional
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.security import get_password_hash, verify_password
from app.models.user.model import  User, UserStatus, UserUpdate, UserRegister

from app.utils import apply_updates


async def register_user(
    *, session: AsyncSession, user_register: UserRegister
) -> User:
    db_obj = User.model_validate(
        user_register, update={"hashed_password": get_password_hash(user_register.password), "status": UserStatus.BASIC}
    )

    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)

    return db_obj


async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(password)
        
    await apply_updates(db_user, user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    session_user = result.scalars().first()
    return session_user


async def get_user_by_id(*, session: AsyncSession, id: uuid.UUID) -> User | None:
    statement = select(User).where(User.id == id)
    result = await session.execute(statement)
    session_user = result.scalars().first()
    return session_user


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


async def get_or_create_user(*, session: AsyncSession, user_register: UserRegister) -> User:
    db_user = await get_user_by_email(session=session, email=user_register.email)
    if not db_user:
        db_user = await register_user(session=session, user_register=user_register)
    return db_user
