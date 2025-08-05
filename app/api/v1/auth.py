
from fastapi import APIRouter, Depends
from app.schemas.token import Token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.services.logging_services import LoggingService
from app.services.auth_service import AuthServices
from app.db.session import get_db



logger = LoggingService(__name__).get_logger()

class Authorization():
    # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/auth", tags=["Authorization"])

    @router.post("/login", response_model=Token)
    def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
        '''
        Authenticates user and returns access and refresh token and saves refresh token in db.
        Requires: username and password
        Returns: user_id and token details in pydantic schema.
        '''
        logger.info("POST/auth/login called")
        obj = AuthServices(db)
        record = obj.user_login(form_data)
        return record