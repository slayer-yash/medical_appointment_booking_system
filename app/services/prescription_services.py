from app.services.basic_services import BasicServices
from fastapi import HTTPException
from pydantic import BaseModel
from app.models.doctor import Doctor
from app.models.patients import Patient
from app.models.appointments import Appointment
from app.models.prescriptions import Prescription
from app.models.users import User
from app.services.filter_pagination_services import FilterPaginationService
from app.schemas.prescriptions import PrescriptionURLResponseSchema
from app.utils.logging import Logging
from app.utils.helper import get_payload
from botocore.exceptions import NoCredentialsError
import uuid
from app.config.aws_config import s3, bucket_name

logger = Logging(__name__).get_logger()

class PrescriptionServices(BasicServices):
    def __init__(self, db, model):
        super().__init__(db, model)

    def create_patient_prescription(self, token, appointment_id, prescription):
        '''
        creates prescription record for appointments
        validates only one prescription is generated for an appointment_id,
        if appointment status is cancelled, restricts generating prescription,
        store prescription record to database and prescription file to s3 bucket
        '''
        logger.info(f"create_patient_prescription method called")
        payload = get_payload(token)

        logger.debug(f"payload received: {payload}")
        user_id = payload.get('user_id')
        uuid_user_id = uuid.UUID(user_id)

        user = super().get_record_by_model_id(User, uuid_user_id)
        appointment = super().get_record_by_model_id(Appointment, appointment_id)

        prescription_record = self.db.query(self.model).filter(self.model.appointment_id == appointment_id).first()
        if prescription_record:
            raise HTTPException(
               400, f"Prescription already generated for appointment id: {appointment_id}, unable to generate another prescription" 
            )

        if not user.doctor.id == appointment.doctor_id:
            raise HTTPException(
                400, f"Unable to generate prescription, doctor are allowed to generate prescription for thier appointments only."
            )

        if appointment.status == "cancelled":
            logger.error(f"Appointment already cancelled, can not generate prescription. Appointment_Status: {appointment.status}")
            raise HTTPException(
                400, "Can not generate prescription on cancelled appointments"
            )

        file_name = f"prescriptions/{uuid.uuid4()}_{prescription.filename}"
        logger.debug(f"filename: {file_name}")

        self.store_prescription_on_aws(prescription, file_name)

        new_prescription = Prescription(
            doctor_id = appointment.doctor_id,
            patient_id = appointment.patient_id,
            appointment_id = appointment_id,
            prescription_obj = file_name,
            created_by = uuid_user_id
        )
        logger.debug(f"New prescription generated, prescription: {new_prescription}")

        record = super().add_record_object_to_db(new_prescription)
        
        return record


    def store_prescription_on_aws(self, prescription, file_name):
        '''
        function to store prescription object to s3 bucket
        '''
        logger.info(f"store_prescription_on_aws method started")
        try:
            logger.info(f"Attempting to upload prescription object to s3 bucket")
            s3.upload_fileobj(prescription.file, bucket_name, file_name)
            logger.info(f"prescription uploaded to bucket")
            return 

        except NoCredentialsError:
            logger.error(f"NoCredentialsError occured during file upload to s3")
            raise HTTPException(500, f"NoCredentialsError occured during file upload to s3")

    def fetch_patient_prescriptions(self, patient_id):
        '''
        fetches prescription records for specified patient_id and adds presigned url for each record 
        for accessing prescription file
        '''
        logger.info(f"fetch_patient_prescriptions method called")

        prescriptions = self.db.query(self.model).filter(self.model.patient_id == patient_id).all()
        logger.debug(f"prescriptions fetched, prescriptions: {prescriptions}")

        modified_prescriptions = []

        for prescription in prescriptions:
            new_prescription = self.get_presighned_url(prescription, PrescriptionURLResponseSchema)
            modified_prescriptions.append(new_prescription)

        return modified_prescriptions

    def fetch_patient_prescription(self, prescription_id):
        '''
        fetches prescirption of specified id and adds presigned url to return record
        '''
        logger.info(f"fetch_patient_prescription method called")

        prescription = super().get_record_by_id(prescription_id)

        logger.info(f"Attempting to generate url for prescription")
        prescription = self.get_presighned_url(prescription, PrescriptionURLResponseSchema)

        return prescription

    def get_presighned_url(self, object, pyschema):
        '''
        function to generate presigned url for prescition object keys
        '''
        logger.info(f"get_presighned_url method called")
        
        prescription_out = pyschema.model_validate(object)
        prescription_data = prescription_out.model_dump()
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object.prescription_obj},
            ExpiresIn = 600
        )
        logger.debug(f"Url generated : {url}")
        prescription_data['prescription_url'] = url
        prescription = pyschema(**prescription_data)

        return prescription

    def fetch_all_prescriptions(self, filters, sort_by, sort_order, page, limit, allowed_fields, search):
        '''
        returns all prescription records and applies filter and pagination, also adds presigned url to each record
        '''
        logger.info(f"fetch_all_prescriptions method called")

        records = None
        search_filters = None
        if search:
            logger.debug(f"Search term provided: '{search.strip()}'")
            records, search_filters = super().search_record(search.strip())

        obj = FilterPaginationService(self.model, allowed_fields, self.db)
        records, total_records= obj.apply_filter_pagination(filters, sort_by, sort_order, page, limit, records, search_filters)
        logger.info(f"Records fetched for {self.model.__name__}")

        modified_prescriptions = []

        for prescription in records:
            new_prescription = self.get_presighned_url(prescription, PrescriptionURLResponseSchema)
            modified_prescriptions.append(new_prescription)

        return modified_prescriptions, total_records
        
        
        