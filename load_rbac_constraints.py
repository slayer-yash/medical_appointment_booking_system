
from app.db.database import engine
from sqlalchemy.orm import sessionmaker
from app.models.rbac import Endpoint


Session = sessionmaker(bind=engine)
session = Session()


get_update_patient_profile = Endpoint(endpoint="/patients/me", methods=["GET", "PATCH"], roles=["patient"])
get_update_doctor_slots = Endpoint(endpoint="/doctor_slots/me", methods=["GET", "PATCH"], roles=["doctor"])

# session.add()
# session.commit()
print("endpoint updated")

session.close()