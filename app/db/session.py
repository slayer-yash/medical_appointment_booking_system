from sqlalchemy.orm import sessionmaker
from app.db.database import engine

local_session = sessionmaker(bind=engine)

def get_db():
    try:
        db = local_session()
        yield db
    finally:
        db.close()