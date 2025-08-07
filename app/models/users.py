import re
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, validates
from app.models.base_model import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(10), unique=True, nullable=False)
    role = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)

    doctor = relationship("Doctor", back_populates="user", uselist=False, foreign_keys="Doctor.user_id")
    patient = relationship("Patient", back_populates="user", uselist=False, foreign_keys="Patient.user_id")
    attendances = relationship("Attendance", back_populates="user", foreign_keys="attendances.user_id")
    

    @validates('first_name')
    def validate_username(self, key, value):
        if value:
            if not value.isalpha():
                raise ValueError(f"first name should be a valid string")
            return value

    @validates('username')
    def validate_username(self, key, value):
        if value:
            pattern = r"^(?=.*[a-zA-Z])[a-zA-Z0-9_]+$"
            if len(value) < 4:
                raise ValueError(f"username must be atlest 3 characters")
            if not re.fullmatch(pattern, value):
                raise ValueError(f"name should be a valid string")
            return value

    @validates('email')
    def validate_email(self,key,email):
        if email:
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, email):
                raise ValueError(f"Invalid email id")
            return email

    @validates('phone')
    def validate_phone(self, key, phone):
        if phone:
            if len(phone) < 10 or len(phone) > 10:
                raise ValueError(f"phone number must be 10 digits only")
            if not phone.isdigit():
                raise ValueError(f"phone number should be only numeric values")
            return phone
    