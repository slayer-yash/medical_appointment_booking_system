from app.models.appointments import Appointment
from app.models.doctor_slots import DoctorSlot
from app.models.doctor import Doctor
from app.models.patients import Patient
from app.models.prescriptions import Prescription
from app.models.users import User

#Used for search field to search accross other models based on relationships
search_parameters = {
    Appointment: {
        'self': ['doctor_id', 'patient_id', 'slot_id', 'status'],
        'relationships': {
            'doctor': ['speciality', 'user_id'],
            'patient': ['user_id'],
            'slot': ['start_time', 'end_time', 'notes', 'is_booked']
        }
    },
    DoctorSlot: {
        'self': ['start_time', 'end_time', 'notes', 'is_booked'],
        'relationships': {
            'doctor': ['speciality', 'user_id'],
            'appointment': ['doctor_id', 'patient_id', 'slot_id', 'status']
        }
    },
    Doctor: {
        'self': ['speciality', 'user_id'],
        'relationships': {
            'appointments': ['doctor_id', 'patient_id', 'slot_id', 'status'],
            'prescriptions': ['doctor_id', 'patient_id', 'appointment_id'],
            'available_slots': ['start_time', 'end_time', 'notes', 'is_booked'],
            'user': ['username', 'first_name', 'last_name', 'email', 'phone']
        }
    },
    Patient: {
        'self': ['user_id'],
        'relationships': {
            'appointments': ['doctor_id', 'patient_id', 'slot_id', 'status'],
            'prescriptions': ['doctor_id', 'patient_id', 'appointment_id'],
            'user': ['username', 'first_name', 'last_name', 'email', 'phone']
        }
    },
    Prescription: {
        'self': ['doctor_id', 'patient_id', 'appointment_id'],
        'relationships': {
            'doctor': ['speciality', 'user_id'],
            'patient': ['user_id']
        }
    },
    User: {
        'self': ['username', 'first_name', 'last_name', 'email', 'phone'],
        'relationships': {
            'doctor': ['speciality', 'user_id'],
            'patient': ['user_id']
        }
    }
}
