# models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, TIMESTAMP
from sqlalchemy.sql import func
from database import Base
import enum



class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    top_k = Column(Integer, default=20)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)
    base_name = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(64), default="coaster")
    difficulty = Column(String(32))
    tags = Column(String(512))
    top_image_path = Column(String(512), nullable=False)
    bot_image_path = Column(String(512))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    model_code = Column(String(64))
    query_text = Column(Text)
    image_name = Column(String(255))
    result_ids = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
