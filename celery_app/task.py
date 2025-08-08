from celery import Celery
import smtplib
from email.message import EmailMessage
from app.models.appointments import Appointment
from app.config.config import EMAIL, PASSWORD
from app.utils.logging import Logging
from celery.schedules import crontab
from app.db.session import local_session

logger = Logging(__name__).get_logger()

c_app = Celery('task', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

c_app.conf.timezone = 'Asia/Kolkata'

c_app.conf.beat_schedule={
    'generate-daily-report': {
        'task': 'celery_app.report_task.generate_daily_appointment_report',
        'schedule': crontab(hour=8, minute=0),
        # 'schedule': 60.0,
    },
    'generate-weekly-report': {
        'task': 'celery_app.report_task.generate_weekly_appointment_report',
        'schedule': crontab(hour=8, minute=0, day_of_week=5),
        # 'schedule': 60.0,
    }
}

EMAIL_ADDRESS = EMAIL
EMAIL_PASSWORD = PASSWORD

@c_app.task
def send_mail(to_mail, subject, body, appointment_id):
    logger.info(f"send_mail method started")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_mail
    msg.set_content(body)
    logger.debug(f"mail parameter: Subject:{subject}, from: {EMAIL_ADDRESS}, to: {to_mail}, body: {body}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    logger.info(f"Send_mail task completed")

    try:
        logger.info(f"Fetching appointment object from database")
        session = local_session()
        appointment = session.query(Appointment).filter(id==appointment_id).first()
        appointment.is_mail_sent = True
        session.commit()
        logger.info(f"mail sent status updated in the database")

    except Exception as e:
        logger.error(f"Error during updating is_mail_sent field in database")

from celery_app import report_task
