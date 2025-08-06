
from schemas.token import Token
from fastapi import APIRouter
from app.utils.logging import Logging
from app.services.auth_service import AuthServices
from app.db.session import get_db
from typing import Annotated


logger = Logging(__name__).get_logger()

class Appointment():
    router = APIRouter(prefix="/appointments", tags=["Appointment"])

    @router.post("/book", response_model=Token)
    def book_appointment():
        pass