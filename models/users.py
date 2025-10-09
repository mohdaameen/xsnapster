from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from db.base import Base
from datetime import datetime, timedelta


def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    phone_number = Column(String, unique=True, nullable=True, index=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    otps = relationship("OTP", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")





class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    otp_code = Column(String, nullable=False)
    for_field = Column(String, nullable=False)  # 'email' or 'phone'
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="otps")

    @staticmethod
    def create_expiry(minutes=5):
        return datetime.utcnow() + timedelta(minutes=minutes)
