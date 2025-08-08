from app.db.session import local_session
from app.models.appointments import Appointment
from app.models.doctor_slots import DoctorSlot
from app.models.doctor import Doctor
from app.models.patients import Patient
from celery_app.task import c_app
from app.utils.logging import Logging
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from app.config.aws_config import s3, bucket_name
from botocore.exceptions import NoCredentialsError
import os
import pytz

ist_timezone = pytz.timezone('Asia/Kolkata')

logging = Logging(__name__).get_logger()

@c_app.task(name="celery_app.report_task.generate_daily_appointment_report")
def generate_daily_appointment_report():
    try:
        logging.info("Started generate_daily_appointment_report method")
        output_dir = "app/reports"
        os.makedirs(output_dir, exist_ok=True)

        today = datetime.now(ist_timezone).date()
        filename = f"daily_appointment_report_{today}.pdf"
        file_path = os.path.join(output_dir, filename)

        pdf = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 50, "Daily Appointment Report")

        pdf.setFont("Helvetica", 12)

        session = local_session()
        start_time = datetime.combine(today, datetime.min.time())
        end_time = datetime.combine(today, datetime.max.time())

        appointments = session.query(Appointment).join(DoctorSlot).filter(DoctorSlot.start_time >= start_time, DoctorSlot.end_time <= end_time).all()
        total_appointments = len(appointments)

        pdf.drawString(50, height - 100, f"Date: {today.strftime('%Y-%m-%d')}")
        pdf.drawString(50, height - 120, f"Total Appointments: {total_appointments}")

        y = height - 150
        for i, appt in enumerate(appointments, start=1):
            doctor_name = appt.doctor.user.first_name + " " + (appt.doctor.user.last_name or "")
            patient_name = appt.patient.user.first_name + " " + (appt.patient.user.last_name or "")
            pdf.drawString(50, y, f"{i}. {appt.slot.start_time.strftime('%H:%M')} - Dr. {doctor_name} with {patient_name}")
            y -= 20
            if y < 100:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y = height - 50

        pdf.save()
        logging.info("Daily appointment report generated successfully.")
        logging.debug(f"File saved at: {file_path}")

        try:
            logging.info(f"Attempting to upload report object to s3 bucket")
            with open(file_path, "rb") as f:
                s3.upload_fileobj(f, bucket_name, 'reports/'+filename)
        except NoCredentialsError:
            logging.error(f"NoCredentialsError occured during file upload to s3")

    except Exception as e:
        logging.exception("Error during daily appointment report generation.")
    finally:
        session.close()

@c_app.task(name="celery_app.report_task.generate_weekly_appointment_report")
def generate_weekly_appointment_report():
    try:
        logging.info("Started generate_weekly_appointment_report method")
        output_dir = "app/reports"
        os.makedirs(output_dir, exist_ok=True)

        today = datetime.now(ist_timezone).date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        filename = f"weekly_appointment_report_{week_start}_to_{week_end}.pdf"
        file_path = os.path.join(output_dir, filename)

        pdf = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 50, "Weekly Appointment Report")

        pdf.setFont("Helvetica", 12)

        session = local_session()
        start_time = datetime.combine(week_start, datetime.min.time())
        end_time = datetime.combine(week_end, datetime.max.time())

        appointments = session.query(Appointment).join(DoctorSlot).filter(DoctorSlot.start_time >= start_time, DoctorSlot.end_time <= end_time).all()
        total_appointments = len(appointments)

        pdf.drawString(50, height - 100, f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        pdf.drawString(50, height - 120, f"Total Appointments: {total_appointments}")

        y = height - 150
        for i, appt in enumerate(appointments, start=1):
            doctor_name = appt.doctor.user.first_name + " " + (appt.doctor.user.last_name or "")
            patient_name = appt.patient.user.first_name + " " + (appt.patient.user.last_name or "")
            pdf.drawString(50, y, f"{i}. {appt.slot.start_time.strftime('%Y-%m-%d %H:%M')} - Dr. {doctor_name} with {patient_name}")
            y -= 20
            if y < 100:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y = height - 50

        pdf.save()
        logging.info("Weekly appointment report generated successfully.")
        logging.debug(f"File saved at: {file_path}")

        try:
            logging.info(f"Attempting to upload report object to s3 bucket")
            with open(file_path, "rb") as f:
                s3.upload_fileobj(f, bucket_name, 'reports/'+filename)
        except NoCredentialsError:
            logging.error(f"NoCredentialsError occured during file upload to s3")
            

    except Exception as e:
        logging.exception("Error during weekly appointment report generation.")
    finally:
        session.close()
