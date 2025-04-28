from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.models.user.model import Message
from app.core.security import get_password_hash
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    status_code=201,
)
async def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = await generate_test_email(email_to=email_to)
    send_email(
        email_address=email_to,
        subject=email_data.subject,
        html_template=email_data.html_content
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.post("/generate-password-hash")
async def generate_password_hash(password:Message) -> str:
    password = password.model_dump()
    hashed_password = get_password_hash(password=password['message'])
    return hashed_password