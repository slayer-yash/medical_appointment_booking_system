
from fastapi import APIRouter, Depends, Query, status
from app.utils.logging import Logging
from app.services.doctor_services import DoctorServices
from app.schemas.doctor import AvailableDoctorResponseSchema, DoctorResponseSchema
from app.schemas.api_response import APIResponse
from app.models.doctor import Doctor as DoctorModel
from app.db.session import get_db
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime


logger = Logging(__name__).get_logger()

class Doctor():

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/doctors", tags=["Doctor"])

    @router.get("/available", response_model=APIResponse[list[AvailableDoctorResponseSchema]])
    def get_available_doctors(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"Get/doctors/available api called")

        obj = DoctorServices(db, DoctorModel)
        records = obj.fetch_doctors(token)

        return APIResponse[list[AvailableDoctorResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message="Doctors with available slots fetched",
            data=records
        )


    @router.get("/", response_model=APIResponse[list[DoctorResponseSchema]])
    def get_all_doctors(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"Get/doctors/ api called")

        obj = DoctorServices(db, DoctorModel)
        records = obj.fetch_doctors(token)

        return APIResponse[list[DoctorResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message="All Doctors fetched",
            data=records
        )



        