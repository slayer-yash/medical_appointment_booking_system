from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.utils.logging import Logging
from app.models.attendance import Attendance as AttendanceModel
from app.schemas.attendances import AttendanceResponseSchema
from app.services.attendance_services import AttendanceServices
from app.schemas.api_response import APIResponse
from app.db.session import get_db
from typing import Annotated
from uuid import UUID


logger = Logging(__name__).get_logger()

class Attendance():
    
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/attendances", tags=["Attendance"])

    @router.post("/time_in", response_model=APIResponse[AttendanceResponseSchema])
    async def user_attendance_time_in(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        '''
        marks attendance time_in for current logged in user
        role: 'nurse', 'doctor'
        '''
        logger.info(f"POST/attendances/time_in API accessed")

        obj = AttendanceServices(db, AttendanceModel)
        record = obj.generate_user_attendance(token)

        return APIResponse[AttendanceResponseSchema](
            success=True,
            status_code=status.HTTP_201_CREATED,
            message=f"User attendance time in saved",
            data=record
        )

    @router.post("/time_out", response_model=APIResponse[AttendanceResponseSchema])
    async def user_attendance_time_out(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session =Depends(get_db)
    ):
        '''
        marks attendance time_out for current logged in user
        role: 'nurse', 'doctor'
        '''
        logger.info(f"Post/ attendances/time_out API accessed")

        obj = AttendanceServices(db, AttendanceModel)
        record = obj.update_user_timeout(token)

        return APIResponse[AttendanceResponseSchema](
            success=True,
            status_code=status.HTTP_201_CREATED,
            message=f"User attendance time out saved",
            data=record
        )