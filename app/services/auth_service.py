from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.token import Token
from app.models.users import User
from app.utils.helper import verify_password, create_token, get_payload
from datetime import timedelta
from app.config.config import ACCESS_TOKEN_EXPIRY_MINUTES, REFRESH_TOKEN_EXPIRY_DAYS
from app.services.logging_services import LoggingService
from app.services.basic_services import BasicServices
# from app.exceptions.basic_exceptions import *
# from app.exceptions.base import AppException
import uuid

logger = LoggingService(__name__).get_logger()

class AuthServices(BasicServices):
    '''
    authorization services available, such as authenticate user, generate tokens, refresh tokens
    '''
    def __init__(self, db, model=None):
        super().__init__(db, model)

    def user_login(self, form_data):
        '''
        validates username and password and create tokens for user
        returns: tokens details in pydantic model.
        '''
        
        user = self.validate_login_credentials(form_data)
        record = self.create_tokens(user)
        return record

    def validate_login_credentials(self, form_data):
        
        '''validates username and password and if validated, returns the user object'''

        logger.info(f"Attempting login for user: {form_data.username}")
        user = self.db.query(User).filter(User.username == form_data.username).first()

        #Uses utility function to verify entered password and stored bcypt password
        if user is None or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid login attempt for username: {form_data.username}")
            raise HTTPException(401, f"Invalid login attempt for username: {form_data.username}")

        return user
        
    def create_tokens(self, user):

        '''
        Creates user access and refresh token, And saves refresh token in database
        returns token details as pydantic model
        '''
        try:
            user_data = {
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'user_id': str(user.id),
                'role': user.role
            }

            logger.info(f"Attempting to create access token")
            access_token = create_token(user_data, expiry=timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES))
            
            logger.info(f"Attempting to createe refresh token")
            refresh_token = create_token(user_data, expiry=timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS), token_type='refresh')

            logger.info(f"Token generated successfully for user: {user.username}")

            user.refresh_token = refresh_token
            self.db.commit()
            logger.info(f"Refresh token stored in database")
            
            return Token(
                user_id = str(user.id),
                username=user.username,
                access_token=access_token,
                refresh_token=refresh_token
            )

        except Exception as e:
            logger.exception(f"Unexpected error during token generation for user: {user.username}: {e}")
            raise HTTPException(500, f"Unexpected error during token generation for user: {user.username}")

    def validate_refresh_token(self, token):
        '''
        Verifies that refresh token is passed in auth header,
        fetches user based on user_id from token, 
        if refresh token is not available in database, 
        it means it is already invalidated by calling /auth/logout api.
        '''        
        try:
            logger.info(f"Validate user token method started")
            payload = get_payload(token)
            logger.debug(f"payload received: {payload}")
            token_type = payload['type']
            user_id = payload['user_id']
            uuid_user_id = uuid.UUID(user_id)
            
            logger.debug(f"Fetched token type and user_id from payload: {token_type}, {user_id}")
            if token_type != 'refresh':
                logger.debug(f"Token type is not refresh, token_type={token_type}")
                raise HTTPException()

            logger.info(f"Fetching user by user_id of payload")
            user = super().get_record_by_id(uuid_user_id)

            logger.info(f"User fetched based on user_id in token")

            if not user.refresh_token == token:
                logger.warning(f"Refresh token already invalidated")
                raise HTTPException()
            return user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException()

    def refresh_user_token(self, token):
        '''validates refresh token and generates new access and refresh token for user, returns tokens in pydantic model'''
        user = self.validate_refresh_token(token)
        record = self.create_tokens(user)
        return record

    def revoke_user_tokens(self, token):
        '''
        validates refresh token and removes refresh_token from database to invalid it
        if refresh_token not found in db it means it is invalidated.
        '''
        try:
            user = self.validate_refresh_token(token)

            user.refresh_token = None
            self.db.commit()
            logger.info(f"Refresh token invalidated")

            return {'message': "Logout successful"}

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(500, "Some error occured")