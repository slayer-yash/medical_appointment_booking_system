from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import jwt
from app.config.config import SECRET_KEY, TOKEN_ALGORITHM
from app.models.users import User
from app.services.logging_services import LoggingService


logger = LoggingService(__name__).get_logger()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_password_hash(pwd) -> str:
    return pwd_context.hash(pwd)

def verify_password(current_password, correct_password):
    return pwd_context.verify(current_password, correct_password)

def create_token(user_data, expiry: timedelta, token_type:str = "access"):
    user_data['exp'] = datetime.now(timezone.utc) + expiry
    user_data['type'] = token_type
    token = jwt.encode(user_data, SECRET_KEY, TOKEN_ALGORITHM)
    logger.debug(f"Created token for user: {token}")
    return token

def get_payload(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=TOKEN_ALGORITHM)
    return payload