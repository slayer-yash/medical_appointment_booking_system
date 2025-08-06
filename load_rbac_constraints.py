
from app.db.database import engine
from sqlalchemy.orm import sessionmaker
from app.models.rbac import Endpoint


Session = sessionmaker(bind=engine)
session = Session()


get_update_patient_profile = Endpoint(endpoint="/patients/me", methods=["GET", "PATCH"], roles=["patient"])
get_update_doctor_slots = Endpoint(endpoint="/doctor_slots/me", methods=["GET", "PATCH"], roles=["doctor"])
get_available_doctors = Endpoint(endpoint="/doctors/available", methods=["GET"], roles=["patient"])
get_doctors = Endpoint(endpoint="/doctors/", methods=["GET"], roles=["patient", "doctor", "nurse"])
get_doctor_available_slot_by_id = Endpoint(endpoint="/doctors/*/available_slots", methods=["GET"], roles=["patient"])



# session.add()
# session.commit()
print("endpoint updated")

session.close()