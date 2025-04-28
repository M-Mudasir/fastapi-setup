import logging
import uuid
from typing import Any
from fastapi import HTTPException

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.models.user import crud    
from app.api.deps import (
    CurrentUser,
    SessionDep
)
from app.core.security import get_password_hash, verify_password
from app.models.user.model import (
    Message,
    UpdatePassword,
    User,
    UserPublic,
    UserUpdate,
    UserRegister,
)

from app.utils import generate_user_created_email

router = APIRouter(prefix="/users", tags=["user"])


@router.post("/signup", response_model=UserPublic)
async def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """

    user = await crud.get_user_by_email(session=session, email=user_in.email.lower())
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    user_register = UserRegister.model_validate(user_in)
    user = await crud.register_user(session=session, user_register=user_register)

    try:
        await generate_user_created_email(
            email_to=user_in.email, 
            name=user_in.first_name, 
        )

    except Exception as e:
        logging.error(f"Failed to send welcome email: {str(e)}")



@router.get("/me", response_model=UserPublic)
async def read_user_me(
    current_user: CurrentUser
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    *, session: SessionDep, user_in: UserUpdate, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        existing_user = await crud.get_user_by_email(session=session, email=user_in.email.lower())
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
        
    existing_user = current_user.model_dump(exclude={"password"})
    user_data = user_in.model_dump(exclude_unset=True)
    
    await crud.update_user(session=session, db_user=current_user, user_in=user_in)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete("/me", response_model=Message)
async def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    await session.delete(current_user)
    await session.commit()
    return Message(message="User deleted successfully")



@router.patch("/me/password", response_model=Message)
async def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    await session.commit()
    return Message(message="Password updated successfully")


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.get_user_by_id(session=session, id=user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user == current_user:
        return user

    return user


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
)
async def update_user(
    *, session: SessionDep, user_id: uuid.UUID, user_in: UserUpdate, current_user: CurrentUser
) -> Any:
    """
    Update a user.
    """
    current_user_id = current_user.id
    db_user = await crud.get_user_by_id(session=session, id=user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = await crud.get_user_by_email(session=session, email=user_in.email.lower())
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    db_user = await crud.update_user(session=session, db_user=db_user, user_in=user_in)
    updated_user = UserPublic(**db_user.model_dump())

    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    current_user_id = current_user.id
    result = await session.execute(
        select(User).where(User.id == user_id)
        )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    await session.delete(user)
    await session.commit()
    
    return Message(message="User deleted successfully")
