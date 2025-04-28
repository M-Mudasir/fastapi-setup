import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings
from app.services.email_service import send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmailData:
    html_content: str
    subject: str

def format_date(date: datetime) -> str:
    return date.strftime("%B %d, %Y at %I:%M %p")

def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


async def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


async def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


async def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None

async def apply_updates(obj, update_data: dict):
    for key, value in update_data.items():
        setattr(obj, key, value)

def null_bearer_token():
    return "Bearer token not found for the user."


async def generate_reset_password_email(email_to: str, token: str, name: str) -> EmailData:
    """
    Generate email for password reset.
    
    Args:
        email_to: Recipient's email address
        token: Password reset token
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password Reset"
    
    base_url = settings.FRONTEND_URL
    password_reset_url = f"{base_url}/reset-password?token={token}"
    
    html_content = render_email_template(
        template_name="password_recovery.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "email": email_to, 
            "name": name,
            "password_reset_url": password_reset_url,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
        },
    )
    await send_email(
        email_address=email_to,
        subject=subject,
        html_template=html_content
    )

async def generate_user_created_email(email_to: str, name: str, organization_name: str) -> EmailData:
    """
    Generate welcome email for a newly created user.
    
    Args:
        email_to: Recipient's email address
        name: User's name
        organization_name: Name of the organization
    """
    project_name = settings.PROJECT_NAME
    subject = f"Welcome to {project_name}"
    
    login_url = f"{settings.FRONTEND_URL}/login"
    
    html_content = render_email_template(
        template_name="user_created.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "email": email_to,
            "name": name,
            "organization_name": organization_name,
            "login_url": login_url,
        },
    )
    await send_email(
        email_address=email_to,
        subject=subject,
        html_template=html_content
    )
    
