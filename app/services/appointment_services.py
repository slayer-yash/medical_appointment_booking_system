from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.token import Token
from app.models.doctor_slots import DoctorSlot
from app.models.doctor import Doctor
from app.models.patients import Patient
from app.models.appointments import Appointment
from app.models.users import User
from app.utils.helper import get_payload
from celery_app.task import send_mail
from datetime import timedelta, datetime, timezone
from app.utils.logging import Logging
from app.services.basic_services import BasicServices
from app.services.filter_pagination_services import FilterPaginationService
from sqlalchemy import and_
import uuid
import pytz

# Define the IST timezone
ist_timezone = pytz.timezone('Asia/Kolkata')


logger = Logging(__name__).get_logger()

class AppointmentServices(BasicServices):
    '''
    Appointment related services : book_appointment, cancel_appointment, fetch_appointments
    '''
    def __init__(self, db, model):
        super().__init__(db, model)


    def book_patient_appointment(self, token, slot_id):
        """
        Checks slot if available or not and then creates appointment
        requires: token and slot_id
        returns: appointment object
        """
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
            appointment = super().add_record_object_to_db(appointment)
            logger.info(f"Appointment added to database")

            logger.info(f"Attempting to set slot object is_booked to True and adding notes")
            slot.is_booked = True
            slot.notes = f"Appointment booked by user : {user_id}"
            logger.info(f"slot object updated")

            super().records_modified(slot, uuid_user_id)

            '''sending mail to user on successful appointment booking'''
            send_mail.apply_async((
                user.email,
                "Appointment booked ",
                f"Dear {user.first_name}, \nYour appointment is booked with doctor {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}\nAppointment id: {appointment.id} \nTime: {appointment.slot.start_time}   \n\n\nThank you,\nOnline Appointment Booking System",
                appointment.id
            ))
            
            return appointment
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error occured during adding appointment to database: {e}")
            raise HTTPException(500, f"Error occured during adding appointment to database")

    def validate_slot_for_appointment_booking(self, slot):
        '''function to check if the given slot is available and if the slot time
        is not in the past'''
        logger.info(f"validate_slot_for_appointment_booking method called")

        self.check_available_slot(slot)
        if self.check_slot_time_not_in_past(slot):
            raise HTTPException(
                400, "Slot Start time is in the past"
            )
    
    def check_available_slot(self, slot):
        '''checks and raises exception if given slot is not already booked'''
        logger.info(f"check_available_slot method called")
        if slot.is_booked:
            logger.error(f"Slot is already booked, slot: {slot}")
            raise HTTPException(
                400, f"Unable to book appointment between {slot.start_time} and {slot.end_time}, slot with id {slot.id} is already booked"
            )

    def check_slot_time_not_in_past(self, slot):
        '''function that checks and converts slot timezone for comparision 
        and returns true if the slot time is in the past'''
        logger.info(f"Checking if slot start_time is not in the past")
        current_time = datetime.now(ist_timezone)
        if slot.start_time.tzinfo is None or slot.start_time.tzinfo.utcoffset(slot.start_time) is None:
            logger.warning("slot.start_time is naive. Localizing it to IST.")
            slot_start_time = ist_timezone.localize(slot.start_time)
        else:
            slot_start_time = slot.start_time
        if slot_start_time < current_time:
            return True
        
    def cancel_patient_appointment(self, token, appointment_id):
        '''canceles the appointment and updates the appointment slot to avaialble
        if the appointment slot was in the future
        '''
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

            if self.check_slot_time_not_in_past(appointment.slot):
                raise HTTPException(
                400, "Slot Start time is in the past"
            )

            appointment.slot.is_booked = False
            appointment.slot.notes = "appointment cancelled"

            appointment = super().records_modified(appointment, uuid_user_id)
            slot = super().records_modified(appointment.slot, uuid_user_id)
            
            return appointment

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during canceling patient appointment {e}")
            raise HTTPException(f"Error during canceling patient appointment")

    def fetch_user_appointments_history(self, token, filters, sort_by, sort_order, page, limit, allowed_fields, search=None):
        '''fetches past records of appointment based on the user_id stored in the token and then applies
        filter and pagination '''
        logger.info(f"fetch_user_appointments_history method started")
        
        payload = get_payload(token)
        logger.debug(f"payload received: {payload}")
        
        user_id = payload.get('user_id')
        role = payload.get('role')
        uuid_user_id = uuid.UUID(user_id) 

        current_time = datetime.now(ist_timezone)
        logger.debug(f"current_time: {current_time}")

        records = self.db.query(self.model)

        if role == "doctor":
            records = records.join(Doctor).join(DoctorSlot).filter(
                and_(
                    Doctor.user_id == uuid_user_id,
                    DoctorSlot.start_time < current_time
                )
            )
            logger.info(f"appointments fetched from the database for role: {role}")

        if role == "patient":
            records = records.join(Patient).join(DoctorSlot).filter(
                and_(
                    Patient.user_id == uuid_user_id,
                    DoctorSlot.start_time <= current_time
                )
            )
            logger.info(f"appointments fetched from the database for role: {role}")

        obj = FilterPaginationService(self.model, allowed_fields, self.db)
        records, total_records= obj.apply_filter_pagination(filters, sort_by, sort_order, page, limit, records)

        return records, total_records


    def fetch_user_appointments_upcoming(self, token, filters, sort_by, sort_order, page, limit, allowed_fields, search=None):
        '''fetches appointmetns for the logged in user and applies filter and pagination'''
        logger.info(F"fetch_user_appointments_upcoming method started")
        
        payload = get_payload(token)
        logger.debug(f"payload received: {payload}")
        
        user_id = payload.get('user_id')
        role = payload.get('role')
        uuid_user_id = uuid.UUID(user_id) 

        current_time = datetime.now(ist_timezone)
        logger.debug(f"current_time: {current_time}")

        records = self.db.query(self.model)

        if role == "doctor":
            records =records.join(Doctor).join(DoctorSlot).filter(
                and_(
                    Doctor.user_id == uuid_user_id,
                    DoctorSlot.start_time > current_time
                )
            )
            logger.info(f"appointments fetched from the database for role: {role}")

        obj = FilterPaginationService(self.model, allowed_fields, self.db)
        records, total_records= obj.apply_filter_pagination(filters, sort_by, sort_order, page, limit, records)

        return records, total_records
        
    def update_user_appointment_status(self, token, appointment_id, status):
        '''checks the status of the appointment if already cancelled, raises exception
        if status is set to completed but the time slot is in the future raises exception
        Requires: appointment_id: UUID and status:str'''
        logger.info(f"update_user_appointment_status method started")

        payload = get_payload(token)
        logger.debug(f"payload received: {payload}")
        
        user_id = payload.get('user_id')
        uuid_user_id = uuid.UUID(user_id) 

        appointment = super().get_record_by_id(appointment_id)
        logger.debug(f"appointment: {appointment}")

        if appointment.status == "cancelled":
            logger.warning(f"Unable to update, the Appoinment status is already set to 'cancelled' ")
            raise HTTPException(400, "Once cancelled, the appointment status can not be updated")

        if status == "completed" and not self.check_slot_time_not_in_past(appointment.slot):
            logger.warning(f"Attempting to set future appointment status as 'completed'")
            raise HTTPException(400, "Unable to set the future appointment status to 'completed'")


        if status == "cancelled":
            if not self.check_slot_time_not_in_past(appointment.slot):
                logger.info(f"Future appointment cancelled, so updating this slot to available slot")
                appointment.slot.is_booked = False
                appointment.slot.notes = "appointment cancelled"

        appointment.status = status

        logger.info(f"Attempting to update changes in the database")
        appointment = super().records_modified(appointment, uuid_user_id)
        logger.info(f"Changes updated in the database")

        return appointment

    def fetch_all_appointments(self, filters, sort_by, sort_order, page, limit, allowed_fields, search):
        '''fetches all appointments and applies filter and pagination'''
        logger.info(f"fetch_all_appointments method called")

        records = None
        search_filters = None
        if search:
            logger.debug(f"Search term provided: '{search.strip()}'")
            records, search_filters = super().search_record(search.strip())

        obj = FilterPaginationService(self.model, allowed_fields, self.db)
        records= obj.apply_filter_pagination(filters, sort_by, sort_order, page, limit, records, search_filters)
        logger.info(f"Records fetched for {self.model.__name__}")
        return records
    
        