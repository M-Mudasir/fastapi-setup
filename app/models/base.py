from sqlmodel import SQLModel

# Register all Database Models here
from app.models.user.model import User

SQLModel.metadata