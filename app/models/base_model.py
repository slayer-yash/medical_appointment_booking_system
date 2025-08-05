from app.db.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class BaseModel(Base):
    '''
    base class with all the fields that are required for all tables and updated automatically
    all models will inherit this class.
    '''
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.now()) 
    modified_at = Column(DateTime, default=datetime.now())
    modified_by = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"))    
    