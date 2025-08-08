
from sqlalchemy.orm import Session
from app.schemas.token import Token
from fastapi import APIRouter, Depends, status
from app.utils.logging import Logging
from app.services.auth_service import AuthServices
from app.services.patient_services import PatientServices
from app.schemas.api_response import APIResponse
from app.schemas.user import UserResponseSchema, UserUpdateSchema
from app.models.users import User
from app.db.session import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer



logger = Logging(__name__).get_logger()

class Patient():

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/patients", tags=["Patient"])

    @router.get("/me", response_model=APIResponse[UserResponseSchema])
    async def get_current_patient_profile(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"GET/patients/me API accessed")
        obj = PatientServices(db, User)
        record = obj.get_current_patient(token)

        return APIResponse[UserResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Current Logged in Patient fetched",
            data=record
        )

    @router.patch("/me", response_model=APIResponse[UserResponseSchema])
    async def update_current_patient_profile(
        token: Annotated[str, Depends(oauth2_scheme)],
        user:UserUpdateSchema,
        db: Session = Depends(get_db)
    ):
        logger.info(f"PATCH/patients/me API accessed")
        obj = PatientServices(db, User)
        record = obj.update_current_patient(token, user)

        return APIResponse[UserResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Current Logged in Patient profile updated",
            data=record
        )

    