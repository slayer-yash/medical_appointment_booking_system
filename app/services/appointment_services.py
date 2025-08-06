from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.token import Token
from app.models.users import User
from app.utils.helper import verify_password, create_token, get_payload
from datetime import timedelta
from app.config.config import ACCESS_TOKEN_EXPIRY_MINUTES, REFRESH_TOKEN_EXPIRY_DAYS
from app.utils.logging import Logging
from app.services.basic_services import BasicServices
# from app.exceptions.basic_exceptions import *
# from app.exceptions.base import AppException
import uuid

logger = Logging(__name__).get_logger()

class AppointmentServices(BasicServices):
    '''
    authorization services available, such as authenticate user, generate tokens, refresh tokens
    '''
    def __init__(self, db, model):
        super().__init__(db, model)

    

        
