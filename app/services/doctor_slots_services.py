
from fastapi import HTTPException
from sqlalchemy import and_
from app.models.doctor_slots import DoctorSlot
from app.models.doctor import Doctor
from app.services.basic_services import BasicServices
from app.schemas.filters import DateFilterSchema
from app.utils.logging import Logging
from app.utils.helper import get_payload
import uuid
from datetime import datetime


logger = Logging(__name__).get_logger()

class DoctorSlotServices(BasicServices):
    def __init__(self, db, model):
        super().__init__(db, model)


    def get_doctor_available_slots(self, token):
        logger.info(f"get_current_patient method called")
        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        role = payload.get('role')
        
        if role != 'doctor':
            logger.error(f"role does not match with 'doctor', role: {role}")
            raise HTTPException(401, "Only 'doctors' can access this method")

        slots = self.db.query(DoctorSlot).join(Doctor).filter(
            and_(
                Doctor.user_id==user_id,
                DoctorSlot.is_booked==False
            )
        ).all()

        return slots

    def update_doctor_slot(self, token, slot_id, slot_update):
        logger.info(f"update_doctor_slot method called")
        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        role = payload.get('role')
        uuid_user_id = uuid.UUID(user_id)
        
        if role != 'doctor':
            logger.error(f"role does not match with 'doctor', role: {role}")
            raise HTTPException(401, "Only 'doctors' can access this method")

        slot = super().get_record_by_id(slot_id)

        if slot.doctor.user_id != uuid_user_id:
            logger.error(f"unable to update another doctor's slot, user_id: {user_id}, slot.doctor.user_id: {slot.doctor.user_id}")
            raise HTTPException(401, "Doctor can update their own slots only")

        logger.debug(f"Attempting to update doctor slot, parameter: token:{token}, slot_update: {slot_update}")
        for field, value in slot_update.model_dump(exclude_unset=True).items():
            logger.debug(f"field: {field}, value: {value}")
            setattr(slot, field, value)

        self.db.commit()
        self.db.refresh(slot)
        logger.info(f"Doctor slot updated in database.")
        logger.debug(f" Slot: {slot}")
        return slot

    def fetch_doctor_available_slots(self, token, doctor_id, date_filter:DateFilterSchema):

        logger.info(f"fetch_doctor_available_slots method called")

        records = self.db.query(self.model)
        filters = []
        filter_field = getattr(self.model, 'doctor_id')
        filters.append(filter_field == doctor_id)

        if date_filter.start_date:
            start_time:datetime = date_filter.start_date
            start_filter_field = getattr(self.model, 'start_time')
            filters.append(start_filter_field >= start_time)

        if date_filter.end_date:
            end_time:datetime = date_filter.end_date
            end_filter_field = getattr(self.model, 'end_time')
            filters.append(end_filter_field <= end_time)


        records = records.filter(and_(*filters)).all()
        logger.debug(f"records: {records}")
        return records