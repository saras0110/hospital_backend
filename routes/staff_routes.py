# routes/staff_routes.py
from flask import Blueprint, request, jsonify, current_app
from utils import token_required
from database import db
from models import Appointment, User, Patient, Doctor

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/appointments', methods=['GET'])
@token_required
def list_appointments():
    if request.user['role'] != 'staff':
        return jsonify({'message':'only staff'}), 403
    appts = Appointment.query.filter(Appointment.status.in_(['approved','pending'])).all()
    out = []
    for a in appts:
        out.append({
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_name': a.patient.user.name if a.patient and a.patient.user else '',
            'doctor_id': a.doctor_id,
            'doctor_name': a.doctor.user.name if a.doctor and a.doctor.user else '',
            'appointment_time': a.appointment_time.isoformat(),
            'status': a.status
        })
    return jsonify(out)

@staff_bp.route('/generate_letter/<int:appointment_id>', methods=['GET'])
@token_required
def generate_letter(appointment_id):
    if request.user['role'] != 'staff':
        return jsonify({'message':'only staff'}), 403
    a = Appointment.query.get(appointment_id)
    if not a:
        return jsonify({'message':'invalid appointment'}), 404
    # Simple plain text letter; frontend can turn this into downloadable file
    letter = f"""
Appointment Letter
Patient: {a.patient.user.name if a.patient and a.patient.user else a.patient_id}
Doctor: {a.doctor.user.name if a.doctor and a.doctor.user else a.doctor_id}
Date/Time: {a.appointment_time.isoformat()}
Status: {a.status}
"""
    return jsonify({'letter': letter})
