from app.services.basic_services import BasicServices
from pydantic import BaseModel
from app.schemas.user import UserCreateDBSchema
from app.models.doctor import Doctor
from app.services.logging_services import LoggingService


logger = LoggingService(__name__).get_logger()

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
        new_user = super().add_records(user_create)
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


        
        return new_user

    def create_doctor_available_slots(self, doctor):
        pass
    
        