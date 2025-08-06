
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from app.utils.Logging import Logging
from app.services.doctor_slots_services import DoctorSlotServices
from app.schemas.api_response import APIResponse
from app.schemas.slots import AvailableSlotResponseSchema, SlotUpdateSchema
from app.models.doctor_slots import DoctorSlot
from app.db.session import get_db
from uuid import UUID
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer



logger = Logging(__name__).get_logger()

class DoctorSlots():

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/doctor_slots", tags=["Doctor Slots"])

    @router.get("/me", response_model=APIResponse[list[AvailableSlotResponseSchema]])
    def get_current_doctor_available_slots (
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"GET/doctor_slots/me API accessed")
        logger.debug(f"Token: {token}")

        obj = DoctorSlotServices(db, DoctorSlot)
        records = obj.get_doctor_available_slots(token)

        logger.info(f"available slots fetched from database")
        logger.debug(f"Slots: {records}")

        return APIResponse[list[AvailableSlotResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message="Current doctor available slots fetched",
            data=records
        )

    @router.patch("/me", response_model=APIResponse[AvailableSlotResponseSchema])
    def get_current_doctor_available_slots (
        token: Annotated[str, Depends(oauth2_scheme)],
        slot_id: UUID,
        slot_update: SlotUpdateSchema,
        db: Session = Depends(get_db)
    ):
        logger.info(f"Patch/doctor_slots/me API accessed")
        logger.debug(f"Token: {token}")

        obj = DoctorSlotServices(db, DoctorSlot)
        record = obj.update_doctor_slot(token, slot_id, slot_update)

        return APIResponse[AvailableSlotResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Doctor slot updated for slot id: {slot_id}",
            data=record
        )

        