from fastapi import APIRouter
from app.api.v1.registration import Registration
from app.api.v1.auth import Authorization
from app.api.v1.patients import Patient
from app.api.v1.doctor_slots import DoctorSlots
from app.api.v1.doctors import Doctor
from app.api.v1.appointments import Appointment
from app.api.v1.prescriptions import Prescription
from app.api.v1.attendances import Attendance

router = APIRouter()

def get_all_router():
    router.include_router(Registration.router)
    router.include_router(Authorization.router)
    router.include_router(Patient.router)
    router.include_router(DoctorSlots.router)
    router.include_router(Doctor.router)
    router.include_router(Appointment.router)
    router.include_router(Prescription.router)
    router.include_router(Attendance.router)
    return router