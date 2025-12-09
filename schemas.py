# backend/schemas.py
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# Auth

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    display_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: Optional[str]
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Pattern

class PatternBase(BaseModel):
    id: int
    base_name: str
    name: str
    type: Optional[str]
    difficulty: Optional[str]
    tags: Optional[str]
    top_image_url: str
    bot_image_url: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


# Model

class MLModelBase(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    is_default: bool
    top_k: int

    class Config:
        from_attributes = True


# Search

class SearchRequest(BaseModel):
    model_code: str
    query_text: Optional[str] = None
    # image sẽ gửi qua multipart, không khai báo ở đây


class SearchResultItem(BaseModel):
    id: int
    base_name: str
    name: str
    top_image_url: str
    difficulty: Optional[str]
    tags: Optional[str]


class SearchResponse(BaseModel):
    items: List[SearchResultItem]
