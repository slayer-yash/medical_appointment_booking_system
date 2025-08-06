from app.services.basic_services import BasicServices
from pydantic import BaseModel
from app.schemas.user import UserCreateDBSchema
from app.models.doctor import Doctor
from app.utils.logging import Logging


logger = Logging(__name__).get_logger()

class NurseServices(BasicServices):
    def __init__(self, db, model):
        super().__init__(db, model)

    def create_nurse_profile(self, user: BaseModel):
        logger.info(f"create_nurse_profile method started")
        user_data = {**user.model_dump()}

        user_data["role"] = 'nurse'
        user_create = UserCreateDBSchema(**user_data)
        logger.debug(F"user_create object initialized: {user_create}")
        new_user = super().add_record(user_create)

        logger.info(f"nurse profile added to database")
        return new_user