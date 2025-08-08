from pydantic import BaseModel
from fastapi import HTTPException
from app.utils.logging import Logging
from app.models.base_model import BaseModel as Base_Model
from uuid import UUID
from datetime import datetime
import pytz

ist_timezone = pytz.timezone('Asia/Kolkata')

logger = Logging(__name__).get_logger()

class BasicServices:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def add_record(self, py_model: BaseModel):
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

    def add_records(self, models: list[Base_Model]):
        try:
            self.db.add_all(models)
            self.db.commit()
            return models
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Unexpected error while adding records: {e}")
            raise HTTPException(500, f"Error while adding records to database")

    def get_record_by_id(self, request_id: UUID):
        '''fetches record by request_id and if record not found, raises not found exception'''
        logger.debug(f"Fetching {self.model.__name__} with ID {request_id}")
        record = self.db.query(self.model).filter(self.model.id == request_id).first()
        if not record:
            logger.error(f"{self.model.__name__} ID {request_id} not found")
            raise HTTPException(404, f"{self.model.__name__} ID {request_id} not found")
        logger.debug(f"{self.model.__name__} with ID {request_id} fetched successfully")
        return record

    def get_all_records(self):

        logger.info(f"get_all_records called for model: {self.model}")
        records = self.db.query(self.model).all()

        logger.debug(f"Records fetched: {records}")
        return records

    def add_record_object_to_db(self, record):
        logger.info(f"add_record_object_to_db method called")

        try:
            logger.info(f"Attempting to add record")
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            logger.info(f"Record added to database")
            return record

        except Exception as e:
            raise HTTPException(500, "Error during adding record object to database")

    def get_record_by_model_id(self, sql_model, request_id):
        logger.info(f"get_record_by_model_id method called")

        record = self.db.query(sql_model).filter(sql_model.id == request_id).first()
        if not record:
            logger.error(f"{sql_model} ID {request_id} not found")
            raise HTTPException()
        logger.debug(f"{sql_model} with ID {request_id} fetched successfully")
        return record

    def get_records_by_field(self, field, value):
        logger.info(f"get_record_by_field method called")

        records = self.db.query(self.model).filter(self.model.field == value).all()
        if not records:
            logger.error(f"{self.model} field : {field} having value: {value} not found")
            raise HTTPException()
        logger.debug(f"{self.model} field : {field} having value: {value} not found")
        return records

    def records_modified(self, record, user_id):
        '''
        updates the modified_at and modified_by field of object, anytime it is modified.
        requires: the object that is modified as record and user_id of the user updating the record
        returns: the updated record after updating modified_at, modifie_by field
        '''
        try:
            logger.debug(f"Modifying record of {self.model.__name__} by user {user_id}")
            record.modified_at = datetime.now(ist_timezone)
            record.modified_by = user_id
            self.db.commit()
            logger.info(f"Record in {self.model.__name__} modified by user {user_id}")
            return record
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error modifying {self.model.__name__} record: {e}")
            raise HTTPException(500, f"Database Error during modifying {self.model.__name__} record: {e}")