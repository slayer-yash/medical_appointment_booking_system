from app.services.basic_services import BasicServices
from fastapi import HTTPException
from pydantic import BaseModel
from app.schemas.user import UserCreateDBSchema
from app.models.doctor import Doctor
from app.services.logging_services import LoggingService
from app.utils.helper import get_payload


logger = LoggingService(__name__).get_logger()

class PatientServices(BasicServices):
    def __init__(self, db, model):
        super().__init__(db, model)

    def create_patient_profile(self, user: BaseModel):
        logger.info(f"create_patient_profile method started")
        user_data = {**user.model_dump()}

        user_data["role"] = 'patient'
        user_create = UserCreateDBSchema(**user_data)
        logger.debug(F"user_create object initialized: {user_create}")
        new_user = super().add_record(user_create)

        logger.info(f"patient profile added to database")
        return new_user

    def get_current_patient(self, token):
        logger.info(f"get_current_patient method called")
        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        role = payload.get('role')
        

        if role != 'patient':
            logger.error(f"role does not match with 'patient', role: {role}")
            raise HTTPException(401, "Only 'patients' can call this api")

        record = super().get_record_by_id(user_id)
        logger.info(f"patient object received from database")
        return record
        
        