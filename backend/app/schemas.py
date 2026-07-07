from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True


class PaperOut(BaseModel):
    id: str
    title: str | None
    original_filename: str
    status: str
    error_message: str | None
    created_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True


class AskRequest(BaseModel):
    question: str


class SourceOut(BaseModel):
    chunk_id: str
    page_number: int
    section_title: str
    paragraph_start: int
    paragraph_end: int
    source_type: str
    score: str
    text_excerpt: str

    class Config:
        from_attributes = True


class AnswerOut(BaseModel):
    id: str
    mode: str
    answer: str
    tutor_explanation: str | None
    confidence: str
    sources: list[SourceOut]
    created_at: datetime

    class Config:
        from_attributes = True


class PaperDetail(PaperOut):
    page_count: int
    paragraph_count: int
    chunk_count: int
