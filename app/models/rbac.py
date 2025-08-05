
from sqlalchemy import Column, String, ARRAY, Integer
from app.db.base import Base


class Endpoint(Base):
    __tablename__ = 'endpoints'
    id = Column(Integer, primary_key=True)
    endpoint = Column(String)
    methods = Column(ARRAY(String))
    roles = Column(ARRAY(String))