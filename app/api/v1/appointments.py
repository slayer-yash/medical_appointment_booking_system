
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
    async def book_appointment(
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
    async def cancel_appointment(
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

    @router.get("/me/history", response_model=APIResponse[list[AppointmentResponseSchema]])
    async def get_user_appointments_history(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db),
        filters: str = None,
        sort_by: str = None,
        sort_order: str = 'asc',
        page: int = 1,
        limit: int = 5,
    ):
        logger.info(f"Get /appointments/me/history API accessed")

        allowed_fields = ['doctor_id', 'patient_id', 'slot_id', 'status']
        obj = AppointmentServices(db, AppointmentModel)
        records, total_records = obj.fetch_user_appointments_history(token, filters, sort_by, sort_order, page, limit, allowed_fields)

        return APIResponse[list[AppointmentResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Appointment history of current logged in user fetched",
            data=records,
            total_records=total_records,
            current_page=page
        )

    @router.get("/me/upcoming", response_model=APIResponse[list[AppointmentResponseSchema]])
    async def get_user_appointments_upcoming(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db),
        filters: str = None,
        sort_by: str = None,
        sort_order: str = 'asc',
        page: int = 1,
        limit: int = 5,
    ):
        logger.info(f"Get /appointments/me/upcoming API accessed")

        allowed_fields = ['doctor_id', 'patient_id', 'slot_id', 'status']
        obj = AppointmentServices(db, AppointmentModel)
        records, total_records = obj.fetch_user_appointments_upcoming(token, filters, sort_by, sort_order, page, limit, allowed_fields)

        return APIResponse[list[AppointmentResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Upcoming appointments of current logged in user fetched",
            data=records,
            total_records=total_records,
            current_page=page
        )

    @router.patch("/{id}", response_model=APIResponse[AppointmentResponseSchema])
    async def update_appointment_status(
        appointment_id: UUID,
        updated_status: str,
        db: Session = Depends(get_db)
    ):
        logger.info(f"Patch/appointments/id API accessed")

        obj = AppointmentServices(db, AppointmentModel)
        record = obj.update_user_appointment_status(appointment_id, updated_status)

        return APIResponse[AppointmentResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Appointment with appointment id: {appointment_id} updated",
            data=record
        )

    @router.get("/", response_model=APIResponse[list[AppointmentResponseSchema]])
    async def get_all_appointments(
        db: Session = Depends(get_db),
        search: str = None,
        filters: str = None,
        sort_by: str = None,
        sort_order: str = 'asc',
        page: int = 1,
        limit: int = 5,
    ):
        logger.info(f"Get /appointments/ API accessed")

        allowed_fields = ['doctor_id', 'patient_id', 'slot_id', 'status']
        obj = AppointmentServices(db, AppointmentModel)
        records, total_recores = obj.fetch_all_appointments(filters, sort_by, sort_order, page, limit, allowed_fields, search)

        return APIResponse[list[AppointmentResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"All appointments fetched",
            data=records,
            total_records=total_recores,
            current_page=page
        )
        