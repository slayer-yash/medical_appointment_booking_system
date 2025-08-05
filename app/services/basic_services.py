from pydantic import BaseModel
from fastapi import HTTPException
from app.services.logging_services import LoggingService


logger = LoggingService(__name__).get_logger()

class BasicServices:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def add_records(self, py_model: BaseModel):
        '''
        adds records to database
        requires: pydantic model that comes from api and role in case of user registration
        '''
        new_record = self.model(**py_model.model_dump())
        try:
            logger.info(f"Attempting to add new record to {self.model.__name__}")
            self.db.add(new_record)
            self.db.commit()
            self.db.refresh(new_record)
            logger.info(f"Record added successfully to {self.model.__name__}")
            return new_record

        except Exception as e:
            self.db.rollback()
            logger.exception(f"Unexpected error while adding record to {self.model.__name__}: {e}")
            raise HTTPException(500, f"Error while adding record to database: {e}")