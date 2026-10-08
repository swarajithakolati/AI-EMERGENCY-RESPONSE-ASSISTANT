import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="COMMAND_OPERATOR") # COMMAND_OPERATOR, FIELD_RESPONDER, ADMIN
    badge_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
