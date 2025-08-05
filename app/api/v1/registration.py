from fastapi import APIRouter, Depends
from app.schemas.user import UserDoctorCreateSchema, UserResponseSchema, UserCreateSchema
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.helper import create_password_hash
from app.services.basic_services import BasicServices
from app.services.doctor_services import DoctorServices
from app.services.patient_services import PatientServices
from app.services.nurse_services import NurseServices
from app.services.logging_services import LoggingService
from app.models.users import User as UserModel


logger = LoggingService(__name__).get_logger()

class Registration:
    router = APIRouter(tags=["Registration"])

    @router.post("/doctor", response_model=UserResponseSchema)
    def register_doctor(user: UserDoctorCreateSchema, db: Session = Depends(get_db)):
        '''
        Creates user with role='customer' and uploads profile_photo on aws s3 bucket
        Saves aws profile_photo key in db
        Requires: unique username, user_email, user_phone and valid Password with one digit, Uppercase letter, Lowercase letter, special character each.
        Returns: Success message with user details in pydantic response.
        '''
        logger.info("POST /registration/doctor called")
        logger.debug(f"Registering doctor with username: {user.username}")

        #generates hash password to store in db
        hashed_password = create_password_hash(user.hashed_password)
        user.hashed_password = hashed_password

        obj = DoctorServices(db, UserModel)
        response = obj.create_doctor_profile(user)

        logger.info(f"Doctor profile generated: {response.username}, ID: {response.id}")
        return response


    @router.post("/patient", response_model=UserResponseSchema)
    def register_patient(user:UserCreateSchema , db: Session = Depends(get_db)):
        '''
        Creates user with role='customer' and uploads profile_photo on aws s3 bucket
        Saves aws profile_photo key in db
        Requires: unique username, user_email, user_phone and valid Password with one digit, Uppercase letter, Lowercase letter, special character each.
        Returns: Success message with user details in pydantic response.
        '''
        logger.info("POST /registration/patient called")
        logger.debug(f"Registering patient with username: {user.username}")

        #generates hash password to store in db
        hashed_password = create_password_hash(user.hashed_password)
        user.hashed_password = hashed_password

        obj = PatientServices(db, UserModel)
        response = obj.create_patient_profile(user)

        logger.info(f"Pateint profile generated: {response.username}, ID: {response.id}")
        return response

    @router.post("/nurse", response_model=UserResponseSchema)
    def register_nurse(user:UserCreateSchema , db: Session = Depends(get_db)):
        '''
        Creates user with role='customer' and uploads profile_photo on aws s3 bucket
        Saves aws profile_photo key in db
        Requires: unique username, user_email, user_phone and valid Password with one digit, Uppercase letter, Lowercase letter, special character each.
        Returns: Success message with user details in pydantic response.
        '''
        logger.info("POST /registration/nurse called")
        logger.debug(f"Registering nurse with username: {user.username}")

        #generates hash password to store in db
        hashed_password = create_password_hash(user.hashed_password)
        user.hashed_password = hashed_password

        obj = NurseServices(db, UserModel)
        response = obj.create_nurse_profile(user)

        logger.info(f"Nurse profile generated: {response.username}, ID: {response.id}")
        return response