from dotenv import load_dotenv
import os


load_dotenv()

upload_folder = "uploads"

#db url
DB_URL = os.getenv("DB_URL")

#JWT constants
SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM")

#Token configurations
ACCESS_TOKEN_EXPIRY_MINUTES = 30
REFRESH_TOKEN_EXPIRY_DAYS = 14