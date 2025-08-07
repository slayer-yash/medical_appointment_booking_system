from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.token import Token
from app.models.doctor_slots import DoctorSlot
from app.models.doctor import Doctor
from app.models.patients import Patient
from app.models.appointments import Appointment
from app.models.users import User
from app.utils.helper import get_payload
from datetime import timedelta, datetime, timezone
from app.utils.logging import Logging
from app.services.basic_services import BasicServices
from sqlalchemy import and_
import uuid
import pytz

# Define the IST timezone
ist_timezone = pytz.timezone('Asia/Kolkata')


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

            self.validate_slot_for_appointment_booking(slot=slot)
            
            payload = get_payload(token)
            logger.debug(f"payload received: {payload}")
            
            user_id = payload.get('user_id')
            role = payload.get('role')
            uuid_user_id = uuid.UUID(user_id)   

            user = super().get_record_by_model_id(User, uuid_user_id)

            if role != 'patient':
                logger.error(f"role does not match with 'patient', role: {role}")
                raise HTTPException(401, "Only 'patients' can access this method")

            logger.info(f"Creating appointment sqlalchemy object")
            appointment = Appointment(
                doctor_id = slot.doctor_id,
                patient_id = user.patient.id,
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

    def validate_slot_for_appointment_booking(self, slot):
        logger.info(f"validate_slot_for_appointment_booking method called")

        self.check_available_slot(slot)
        self.check_slot_time_not_in_past(slot)
    
    def check_available_slot(self, slot):
        logger.info(f"check_available_slot method called")
        if slot.is_booked:
            logger.error(f"Slot is already booked, slot: {slot}")
            raise HTTPException(
                400, f"Unable to book appointment between {slot.start_time} and {slot.end_time}, slot with id {slot.id} is already booked"
            )

    def check_slot_time_not_in_past(self, slot):
        logger.info(f"Checking if slot start_time is not in the past")
        current_time = datetime.now(ist_timezone)
        if slot.start_time.tzinfo is None or slot.start_time.tzinfo.utcoffset(slot.start_time) is None:
            logger.warning("slot.start_time is naive. Localizing it to IST.")
            slot_start_time = ist_timezone.localize(slot.start_time)
        else:
            slot_start_time = slot.start_time
        if slot_start_time < current_time:
            raise HTTPException(
                400, "Slot Start time is in the past"
            )
        
    def cancel_patient_appointment(self, token, appointment_id):
        logger.info(f"cancel_patient_appointment method called")

        try:
            payload = get_payload(token)
            logger.debug(f"payload received: {payload}")
            
            user_id = payload.get('user_id')
            # role = payload.get('role')
            uuid_user_id = uuid.UUID(user_id) 

            user = super().get_record_by_model_id(User, uuid_user_id)
            appointment = super().get_record_by_id(appointment_id)

            if not user.patient.id == appointment.patient_id:
                logger.error(f"Patient trying to cancel other patient's appointments")
                raise HTTPException(400, f"Patient can only cancel their own appointments")

            if not appointment.status == "booked":
                raise HTTPException(400, f"Unable to cancel appointment, appointment not in status 'booked'. Appointment_status: {appointment.status}")

            appointment.status = "cancelled"

            self.check_slot_time_not_in_past(appointment.slot)

            appointment.slot.is_booked = False
            appointment.slot.notes = "appointment cancelled"
            

            self.db.commit()
            self.db.refresh(appointment)
            
            return appointment

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during canceling patient appointment {e}")
            raise HTTPException(f"Error during canceling patient appointment")

    def fetch_user_appointments_history(self, token):
        
        payload = get_payload(token)
        logger.debug(f"payload received: {payload}")
        
        user_id = payload.get('user_id')
        role = payload.get('role')
        uuid_user_id = uuid.UUID(user_id) 

        current_time = datetime.now(ist_timezone)
        logger.debug(f"current_time: {current_time}")

        if role == "doctor":
            appointments = self.db.query(self.model).join(Doctor).join(DoctorSlot).filter(
                and_(
                    Doctor.user_id == uuid_user_id,
                    DoctorSlot.start_time <= current_time
                )
            )
            logger.info(f"appointments fetched from the database for role: {role}")
            return appointments

        if role == "patient":
            appointments = self.db.query(self.model).join(Patient).join(DoctorSlot).filter(
                and_(
                    Patient.user_id == uuid_user_id,
                    DoctorSlot.start_time <= current_time
                )
            )
            logger.info(f"appointments fetched from the database for role: {role}")
            return appointments

        raise HTTPException(
            500, f"Unable to fetch appointment history, role did not match with 'pateint' or 'doctor'. Role: {role}"
        )
        
            

        