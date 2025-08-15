# models.py
from database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient','doctor','staff'
    name = db.Column(db.String(120))
    photo = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    patient = db.relationship('Patient', back_populates='user', uselist=False)
    doctor = db.relationship('Doctor', back_populates='user', uselist=False)
    staff = db.relationship('Staff', back_populates='user', uselist=False)

class Patient(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    address = db.Column(db.String(256))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    contact = db.Column(db.String(50))
    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient')
    messages = db.relationship('Message', back_populates='patient')
    bills = db.relationship('Bill', back_populates='patient')
    treatments = db.relationship('Treatment', back_populates='patient')

class Doctor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    specialization = db.Column(db.String(120))
    qualification = db.Column(db.String(120))
    date_of_joining = db.Column(db.Date)
    user = db.relationship('User', back_populates='doctor')
    appointments = db.relationship('Appointment', back_populates='doctor')
    messages = db.relationship('Message', back_populates='doctor')
    prescriptions = db.relationship('Prescription', back_populates='doctor')

class Staff(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    qualification = db.Column(db.String(120))
    date_of_joining = db.Column(db.Date)
    user = db.relationship('User', back_populates='staff')

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    appointment_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, approved, done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)
    content = db.Column(db.Text)
    image = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', back_populates='messages')
    doctor = db.relationship('Doctor', back_populates='messages')

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    content = db.Column(db.Text)
    file = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctor = db.relationship('Doctor', back_populates='prescriptions')

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    amount = db.Column(db.Float)
    details = db.Column(db.Text)
    paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', back_populates='bills')

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    start_date = db.Column(db.Date)
    days_estimate = db.Column(db.Integer)
    status = db.Column(db.String(20), default='ongoing')
    medicines = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', back_populates='treatments')
