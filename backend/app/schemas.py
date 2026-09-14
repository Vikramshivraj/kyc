from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    content_type: str
    file_size: int
    status: str