
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.utils.logging import Logging
from app.models.prescriptions import Prescription as PrescriptionModel
from app.services.prescription_services import PrescriptionServices
from app.schemas.api_response import APIResponse
from app.schemas.prescriptions import PrescriptionResponseSchema
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


    @router.get("/patient/{patient_id}", response_model=APIResponse[list[PrescriptionResponseSchema]])
    def get_patient_prescriptions(
        patient_id: UUID,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
    ):
        logger.info(f"Get/prescriptions/patient/patient_id API accessed")

        obj = PrescriptionServices(db, PrescriptionModel)
        records = obj.fetch_patient_prescriptions(patient_id)

        return APIResponse[list[PrescriptionResponseSchema]](
            success=True,
            status_code=status.HTTP_200_OK,
            message=f"prescriptions fetched for patient id: {patient_id}",
            data=records
        )