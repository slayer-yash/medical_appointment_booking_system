from app.services.basic_services import BasicServices
from fastapi import HTTPException
from pydantic import BaseModel
from app.schemas.user import UserCreateDBSchema
from app.models.doctor import Doctor
from app.models.users import User
from app.models.patients import Patient
from app.utils.logging import Logging
from app.utils.helper import get_payload
import uuid


logger = Logging(__name__).get_logger()

class PatientServices(BasicServices):
    def __init__(self, db, model):
        super().__init__(db, model)

    def create_patient_profile(self, user: BaseModel):
        '''
        adds role 'patient' to user and adds record object to database and creates patient record 
        '''
        logger.info(f"create_patient_profile method started")
        user_data = {**user.model_dump()}

        user_data["role"] = 'patient'
        user_create = UserCreateDBSchema(**user_data)
        logger.debug(F"user_create object initialized: {user_create}")
        new_user = super().add_record(user_create)

        logger.info(f"user added to database")

        patient = Patient(
            user_id = new_user.id
        )
        logger.debug(f"Patient profile created: patient: {patient}")

        record = super().add_record_object_to_db(patient)
        
        return new_user

    def get_current_patient(self, token):
        '''
        fetches current logged in patient
        returns: user object
        '''
        logger.info(f"get_current_patient method called")
        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        role = payload.get('role')
        

        if role != 'patient':
            logger.error(f"role does not match with 'patient', role: {role}")
            raise HTTPException(401, "Only 'patients' can access this method")

        record = super().get_record_by_id(user_id)
        logger.info(f"patient object received from database")
        return record


    def update_current_patient(self, token, user_update:BaseModel):
        '''
        fetches current logged in patient and updates user model
        requires: token and user_update model
        returns: updated patient's user record
        '''
        logger.info(f"update_current_patient method called")
        user = self.get_current_patient(token)

        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        uuid_user_id = uuid.UUID(user_id)

        try:
            logger.debug(f"Attempting to update patient profile, parameter: token:{token}, user_update: {user_update}")
            for field, value in user_update.model_dump(exclude_unset=True).items():
                if value:
                    setattr(user, field, value)

            user = super().records_modified(user, uuid_user_id)

            logger.info(f"Patient profile updated in database.")
            logger.debug(f" User: {user}")
            return user

        except Exception as e:
            logger.exception(f"error during update_current_patient method: {e}")
            raise HTTPException(status_code=500, detail="error during updating current patient profile")


        