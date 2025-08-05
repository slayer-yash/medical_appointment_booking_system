
from app.db.database import engine
from sqlalchemy.orm import sessionmaker
from app.models.rbac import Endpoint


Session = sessionmaker(bind=engine)
session = Session()

