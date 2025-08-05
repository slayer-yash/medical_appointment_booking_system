from fastapi import APIRouter
from app.api.v1.registration import Registration
from app.api.v1.auth import Authorization
from app.api.v1.patients import Patient

router = APIRouter()

def get_all_router():
    router.include_router(Registration.router)
    router.include_router(Authorization.router)
    router.include_router(Patient.router)
    return router