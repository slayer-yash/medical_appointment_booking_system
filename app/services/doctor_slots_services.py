
from fastapi import HTTPException
from sqlalchemy import and_
from app.models.doctor_slots import DoctorSlot
from app.models.doctor import Doctor
from app.services.basic_services import BasicServices
from app.services.logging_services import LoggingService
from app.utils.helper import get_payload


logger = LoggingService(__name__).get_logger()

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