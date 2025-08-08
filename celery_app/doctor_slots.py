
from celery_app.task import c_app
from celery import shared_task
from datetime import datetime, timedelta
from app.db.session import local_session
from app.models.doctor import Doctor
from app.models.doctor_slots import DoctorSlot
from app.utils.logging import Logging
from sqlalchemy.orm import joinedload
import pytz

logger = Logging(__name__).get_logger()
ist = pytz.timezone("Asia/Kolkata")


@c_app.task(name="celery_app.doctor_slots.generate_future_doctor_slots")
def generate_future_doctor_slots():
    session = local_session()
    try:
        logger.info("Generating doctor slots for next 5 days...")

        doctors = session.query(Doctor).options(joinedload(Doctor.available_slots)).all()
        current_day = datetime.now(ist).replace(minute=0, second=0, microsecond=0)
        max_day = current_day + timedelta(days=5)

        for doctor in doctors:
            # Get the latest slot
            latest_slot = (
                session.query(DoctorSlot)
                .filter(DoctorSlot.doctor_id == doctor.id)
                .order_by(DoctorSlot.start_time.desc())
                .first()
            )

            # Determine the starting date
            last_slot_day = latest_slot.start_time if latest_slot else current_day - timedelta(days=1)
            slot_start_day = max(last_slot_day + timedelta(days=1), current_day)

            while slot_start_day.date() <= max_day.date():
                slot_hour = slot_start_day.replace(hour=10)
                slot_end_hour = slot_start_day.replace(hour=18)

                while slot_hour < slot_end_hour:
                    # Check if this slot already exists (avoid duplication)
                    existing_slot = session.query(DoctorSlot).filter(
                        DoctorSlot.doctor_id == doctor.id,
                        DoctorSlot.start_time == slot_hour
                    ).first()

                    if not existing_slot:
                        new_slot = DoctorSlot(
                            doctor_id=doctor.id,
                            start_time=slot_hour,
                            end_time=slot_hour + timedelta(hours=1)
                        )
                        session.add(new_slot)
                        logger.debug(f"Created slot: {slot_hour} for Doctor: {doctor.id}")

                    slot_hour += timedelta(hours=1)

                slot_start_day += timedelta(days=1)

        session.commit()
        logger.info("All future doctor slots generated successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error during doctor slot generation: {e}")
    finally:
        session.close()