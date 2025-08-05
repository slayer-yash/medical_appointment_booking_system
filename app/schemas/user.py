from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from fastapi import Form, HTTPException, status
import string
from typing import Optional
import re

class UserCreateSchema(BaseModel):
    username: str = Field(min_length=2, max_length=50, examples=["emily123"])
    hashed_password: Optional[str]
    first_name: str = Field(Field(min_length=2, max_length=50, examples=["Emily"]))
    last_name: Optional[str]
    email: EmailStr
    phone: str = Field(examples=[9898989898])

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    @field_validator("username")
    def validate_name(name):
        if len(name) < 2 or len(name) > 50:
            raise HTTPException(422)
        pattern = r"^(?=.*[a-zA-Z])[a-zA-Z0-9_]+$"
        if not re.fullmatch(pattern, name):
            raise HTTPException(422)
        return name

    @field_validator("first_name")
    def validate_name(name):
        if len(name) < 2 or len(name) > 50:
            raise HTTPException(422)
        if not name.isalpha():
            raise HTTPException(422)
        return name

    @field_validator("last_name")
    def validate_name(name):
        if name:
            if len(name) < 2 or len(name) > 50:
                raise HTTPException(422)
            if not name.isalpha():
                raise HTTPException(422)
        return name

    @field_validator("hashed_password")
    def validate_password(password):
        if len(password) < 8:
            raise HTTPException(422)
        is_upper = is_lower = is_number = has_punctuation = False
        for val in password:
            if val.isupper():
                is_upper=True
            elif val.islower():
                is_lower=True
            elif val.isdigit():
                is_number=True
            elif val in string.punctuation:
                has_punctuation=True
        if not (is_upper and is_lower and is_number and has_punctuation):
            raise HTTPException(422)
        return password
    
    @field_validator("phone")
    def validate_phone(phone):
        if not phone.isdigit():
            raise HTTPException(422)
        if len(phone) != 10:
            raise HTTPException(422)
        return phone

class UserCreateDBSchema(UserCreateSchema):
    role: str

class UserDoctorCreateSchema(UserCreateSchema):
    speciality: str = Field(min_length=2, max_length=50, examples=["Cardiology"])
    


class UserResponseSchema(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True