import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from enum import Enum

class UserStatus(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=255)
    status: UserStatus = UserStatus.BASIC


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = None  
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=255)

# Public schemas should exclude sensitive fields
class UserPublic(UserBase):
    id: uuid.UUID


class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=40)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
