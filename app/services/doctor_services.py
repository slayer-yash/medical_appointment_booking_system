
from fastapi import HTTPException
from app.services.basic_services import BasicServices
from sqlalchemy import and_
from pydantic import BaseModel
from app.schemas.user import UserCreateDBSchema
from app.schemas.filters import DateFilterSchema
from app.models.doctor import Doctor
from app.models.doctor_slots import DoctorSlot
from app.utils.logging import Logging
from datetime import timedelta, datetime
from app.utils.helper import get_payload
from datetime import date


logger = Logging(__name__).get_logger()

class DoctorServices(BasicServices):
    def __init__(self, db, model):
        super().__init__(db, model)

    def create_doctor_profile(self, user: BaseModel):
        logger.info(f"create_doctor_profile method started")
        user_data = {**user.model_dump()}
        speciality = user_data['speciality']
        user_data["role"] = 'doctor'
        
        user_create = UserCreateDBSchema(**user_data)
        logger.debug(F"user_create object initialized: {user_create}")
        new_user = super().add_record(user_create)
        logger.info(f"user added to database, now trying to create doctor profile")
        
        doctor =Doctor(
            user_id = new_user.id,
            speciality = speciality
        )
        logger.debug(f"Doctor profile created: {doctor}")
        
        logger.info(f"Attempting to add doctor profile to database")
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        logger.info(f"doctor profile added to database")

        self.create_doctor_available_slots(doctor)
        
        return new_user

    def create_doctor_available_slots(self, doctor, slot_start_time=10, slot_end_time=18):
        current_day = datetime.today().replace(minute=0, second=0)
        end_day = current_day+timedelta(days=5)
        start_day = current_day
        slots = []

        logger.info(f"Attempting to create slots for doctor")
        while start_day<=end_day:
            slot_start = start_day.replace(hour=slot_start_time)
            last_slot = start_day.replace(hour=slot_end_time-1)
            current_time = datetime.now()
            while slot_start <= last_slot:
                if slot_start < current_time:
                    slot_start+=timedelta(hours=1)
                    continue
                slot_end = slot_start+timedelta(hours=1)
                slot = DoctorSlot(
                    doctor_id=doctor.id,
                    start_time=slot_start,
                    end_time=slot_end
                )
                logger.debug(f"Slot created: {slot}")
                slots.append(slot)
                slot_start+=timedelta(hours=1)
            start_day+=timedelta(days=1)

        super().add_records(slots)
        return slots
    
    def fetch_doctors(self, token):
        logger.info(f"fetch_doctors method called")
        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        role = payload.get('role')
        
        # if role != 'patient':
        #     logger.error(f"role does not match with 'patient', role: {role}")
        #     raise HTTPException(401, "Only 'patients' can access this method")

        doctors = super().get_all_records()
        
        return doctors
