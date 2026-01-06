from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func, Boolean
from sqlalchemy import String
from sqlalchemy import JSON
from database.database_setup import Base


class User(Base):
    __tablename__ = "user_account"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String, default="user")


class Booking(Base):
    __tablename__ = "booking"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_account.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    planning_response = Column(JSON, nullable=True)