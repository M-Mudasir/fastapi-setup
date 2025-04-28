
# TODO: uncomment this when we have a background task to run

# import logging
# import asyncio
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# import httpx

# from .celery_config import celery
# from app.core.config import settings
# from app.models.user.model import UserTokenUpdate
# from app.models.user.crud import get_users_with_expiring_tokens, update_user_token

# logger = logging.getLogger(__name__)

# @celery.task(bind=True, acks_late=True)
# def sample_job(self):
#     """
#     Main Celery task that runs the token refresh logic using async SQLAlchemy
#     """
#     try:
#         asyncio.run(first_task())
#     except Exception as e:
#         logger.error(f"Error in sample_job: {e}")


# async def first_task():
#     """
#     Async logic to refresh tokens for users with expiring tokens
#     """
#     pass