
from fastapi import APIRouter, Depends, status
from app.schemas.token import Token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.users import User
from app.services.logging_services import LoggingService
from app.services.auth_service import AuthServices
from app.schemas.api_response import APIResponse
from app.db.session import get_db
from typing import Annotated


logger = LoggingService(__name__).get_logger()

class Authorization():
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/auth", tags=["Authorization"])

    @router.post("/login", response_model=APIResponse[Token])
    def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
        '''
        Authenticates user and returns access and refresh token and saves refresh token in db.
        Requires: username and password
        Returns: user_id and token details in pydantic schema.
        '''
        logger.info("POST/auth/login called")
        obj = AuthServices(db)
        record = obj.user_login(form_data)
        return APIResponse[Token](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Logged in successfully",
            data=record
        )

    @router.post("/logout", response_model=APIResponse[dict])
    def logout(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
        '''
        Authenticates refresh token and invalidates it by removing it from the db
        Requires: Valid refresh token
        Returns: success message saying logout successful
        '''
        logger.info(f"POST/auth/logout called")
        obj = AuthServices(db, User)
        record = obj.revoke_user_tokens(token)
        return APIResponse[dict](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"user logged out",
            data=record
        )

    @router.post("/refresh-token", response_model=APIResponse[Token])
    def refresh_token(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
        '''
        Authenticates refresh token and returns new access and refresh token and saves refresh token in db
        Requires: Valid refresh token
        Returns: user_id and token details in pydantic schema.
        '''
        logger.info(f"POST/auth/refresh-token called")
        obj = AuthServices(db, User)
        record = obj.refresh_user_token(token)
        return APIResponse[Token](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"user access and refresh token re-generated",
            data=record
        )