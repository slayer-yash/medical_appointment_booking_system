from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.token import Token
from app.models.users import User
from app.models.attendance import Attendance
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

class AttendanceServices(BasicServices):
    '''
    '''
    def __init__(self, db, model):
        super().__init__(db, model)

    def generate_user_attendance(self, token):
        logger.info(f"generate_user_attendance method called")
        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        uuid_user_id = uuid.UUID(user_id)

        new_attendance = Attendance(
            user_id = uuid_user_id,
            created_by = uuid_user_id
        )
        logger.debug(f"attendance object instanitiated: {new_attendance}")
        
        record = super().add_record_object_to_db(new_attendance)

        return record
