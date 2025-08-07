
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.utils.logging import Logging
from app.services.appointment_services import AppointmentServices
from app.models.appointments import Appointment as AppointmentModel
from app.schemas.appointments import AppointmentResponseSchema
from app.schemas.api_response import APIResponse
from app.db.session import get_db
from typing import Annotated
from uuid import UUID


logger = Logging(__name__).get_logger()

class Appointment():
    
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/appointments", tags=["Appointment"])

    @router.post("/book", response_model=APIResponse[AppointmentResponseSchema])
    def book_appointment(
        slot_id: UUID,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"POST/appointments/book API accessed")

        obj = AppointmentServices(db, AppointmentModel)
        record = obj.book_patient_appointment(token, slot_id)

        logger.debug(f"appointment booked, appointment: {record}")

        return APIResponse[AppointmentResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Appointment booked for logged in patient",
            data=record
        )

    @router.post("/{appointment_id}/cancel", response_model=APIResponse[AppointmentResponseSchema])
    def cancel_appointment(
        appointment_id: UUID,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"Post /appointments/{appointment_id}/cancel API accessed")

        obj = AppointmentServices(db, AppointmentModel)
        record = obj.cancel_patient_appointment(token, appointment_id)

        return APIResponse[AppointmentResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Appointment with id: {appointment_id} cancelled for logged in patient",
            data=record
        )