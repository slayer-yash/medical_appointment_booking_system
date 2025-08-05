
from sqlalchemy.orm import Session
from app.schemas.token import Token
from fastapi import APIRouter, Depends, status
from app.services.logging_services import LoggingService
from app.services.auth_service import AuthServices
from app.services.patient_services import PatientServices
from app.schemas.api_response import APIResponse
from app.schemas.user import UserResponseSchema
from app.models.users import User
from app.db.session import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer




logger = LoggingService(__name__).get_logger()

class Patient():

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/patients", tags=["Patient"])

    @router.get("/me", response_model=APIResponse[UserResponseSchema])
    def get_current_patient_profile(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"get_current_patient_profile method started")
        obj = PatientServices(db, User)
        record = obj.get_current_patient(token)

        return APIResponse[UserResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Current Logged in Patient fetched",
            data=record
        )

    