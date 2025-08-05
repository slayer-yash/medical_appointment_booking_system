
from app.db.database import engine
from sqlalchemy.orm import sessionmaker
from app.models.rbac import Endpoint


Session = sessionmaker(bind=engine)
session = Session()


get_patient_profile = Endpoint(endpoint="/patients/me", methods=["GET"], roles=["patient"])

# session.add()
# session.commit()
print("endpoint updated")

session.close()