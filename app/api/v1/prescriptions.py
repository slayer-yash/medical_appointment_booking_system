
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.utils.logging import Logging
from app.models.prescriptions import Prescription as PrescriptionModel
from app.services.prescription_services import PrescriptionServices
from app.schemas.api_response import APIResponse
from app.schemas.prescriptions import PrescriptionResponseSchema, PrescriptionURLResponseSchema
from app.db.session import get_db
from typing import Annotated
from uuid import UUID


logger = Logging(__name__).get_logger()

class Prescription():
    
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    router = APIRouter(prefix="/prescriptions", tags=["Prescription"])

    @router.post("/{appointment_id}", response_model=APIResponse[PrescriptionResponseSchema])
    def add_patient_prescription(
        appointment_id: UUID,
        token: Annotated[str, Depends(oauth2_scheme)],
        prescription: UploadFile = File(...),
        db: Session = Depends(get_db)
    ):
        logger.info(f"POST/prescriptions/appointment_id API accessed")

        obj = PrescriptionServices(db, PrescriptionModel)
        record = obj.create_patient_prescription(token, appointment_id, prescription)

        return APIResponse[PrescriptionResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"Prescription added for appointment id: {appointment_id}",
            data=record
        )


    @router.get("/patient/{patient_id}", response_model=APIResponse[list[PrescriptionURLResponseSchema]])
    def get_patient_prescriptions(
        patient_id: UUID,
        db: Session = Depends(get_db)
    ):
        logger.info(f"Get/prescriptions/patient/patient_id API accessed")

        obj = PrescriptionServices(db, PrescriptionModel)
        records = obj.fetch_patient_prescriptions(patient_id)

        return APIResponse[list[PrescriptionURLResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"prescriptions fetched for patient id: {patient_id}",
            data=records
        )

    @router.get("/{prescription_id}", response_model=APIResponse[PrescriptionURLResponseSchema])
    def get_prescription(
        prescription_id: UUID,
        db: Session = Depends(get_db)
    ):
        logger.info(f"Get/prescriptions/prescription_id API accessed")

        obj = PrescriptionServices(db, PrescriptionModel)
        record = obj.fetch_patient_prescription(prescription_id)

        return APIResponse[PrescriptionURLResponseSchema](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"prescription fetched for priscription id: {prescription_id}",
            data=record
        )

    @router.get("/", response_model=APIResponse[list[PrescriptionURLResponseSchema]])
    def get_all_prescription(
        db: Session = Depends(get_db),
        search: str = None,
        filters: str = None,
        sort_by: str = None,
        sort_order: str = 'asc',
        page: int = 1,
        limit: int = 5,
    ):
        logger.info(f"Get/prescriptions/ API accessed")

        allowed_fields = ['doctor_id', 'patient_id', 'appointment_id']
        obj = PrescriptionServices(db, PrescriptionModel)
        records, total_records = obj.fetch_all_prescriptions(filters, sort_by, sort_order, page, limit, allowed_fields, search)

        return APIResponse[list[PrescriptionURLResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"All prescriptions fetched",
            data=records,
            total_records=total_records,
            current_page=page
        )