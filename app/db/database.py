from sqlalchemy import create_engine
from app.config.config import DB_URL

engine = create_engine(DB_URL)

