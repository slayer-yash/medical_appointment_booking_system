from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.token import Token
from app.models.doctor_slots import DoctorSlot
from app.models.appointments import Appointment
from app.utils.helper import get_payload
from datetime import timedelta
from app.utils.logging import Logging
from app.services.basic_services import BasicServices

import uuid

logger = Logging(__name__).get_logger()

class AppointmentServices(BasicServices):
    '''
    authorization services available, such as authenticate user, generate tokens, refresh tokens
    '''
    def __init__(self, db, model):
        super().__init__(db, model)


    def book_patient_appointment(self, token, slot_id):
        logger.info(f"book_patient_appointment method called")

        try:
            slot = self.db.query(DoctorSlot).filter(DoctorSlot.id == slot_id).first()
            if slot is None:
                logger.error(f"Slot with ID {slot_id} does not exist")
                raise HTTPException(404, f"Slot with ID {slot_id} does not exist")
            
            payload = get_payload(token)
            logger.debug(f"payload received: {payload}")
            
            user_id = payload.get('user_id')
            role = payload.get('role')
            uuid_user_id = uuid.UUID(user_id)        

            if role != 'patient':
                logger.error(f"role does not match with 'patient', role: {role}")
                raise HTTPException(401, "Only 'patients' can access this method")

            logger.info(f"Creating appointment sqlalchemy object")
            appointment = Appointment(
                doctor_id = slot.doctor_id,
                patient_id = uuid_user_id,
                slot_id = slot.id,
                status = 'booked',
                created_by = uuid_user_id
            )
            logger.debug(f"Appointment object: {appointment}")

        
            logger.info(f"Attempting to add appointment to database")
            self.db.add(appointment)
            logger.info(f"Appointment added to database")

            logger.info(f"Attempting to set slot object is_booked to True and adding notes")
            slot.is_booked = True
            slot.notes = f"Appointment booked by user : {user_id}"
            logger.info(f"slot object updated")
            
            self.db.commit()
            self.db.refresh(appointment)
            logger.info(f"Refreshing the appointment object")
            
            return appointment
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error occured during adding appointment to database: {e}")
            raise HTTPException(500, f"Error occured during adding appointment to database")
    

        
