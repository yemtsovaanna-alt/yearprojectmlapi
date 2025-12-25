from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from app.database import Base


class RequestHistory(Base):
    __tablename__ = "request_history"

    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(String, nullable=False)
    processing_time = Column(Float, nullable=False)
    input_data_size = Column(Integer, nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=False)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
