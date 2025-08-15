# routes/doctor_routes.py
from flask import Blueprint, request, jsonify, current_app
from utils import token_required, save_uploaded_file
from database import db
from models import User, Doctor, Patient, Appointment, Message, Prescription, Treatment
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/patients', methods=['GET'])
@token_required
def my_patients():
    if request.user['role'] != 'doctor':
        return jsonify({'message':'only doctor'}), 403
    uid = request.user['user_id']
    appts = Appointment.query.filter_by(doctor_id=uid, status='approved').all()
    # Unique patient list
    pids = set([a.patient_id for a in appts])
    out = []
    for pid in pids:
        user = User.query.get(pid)
        patient = user.patient
        out.append({'id': pid, 'name': user.name, 'photo': user.photo, 'contact': patient.contact})
    return jsonify(out)

@doctor_bp.route('/appointments/pending', methods=['GET'])
@token_required
def pending_appointments():
    if request.user['role'] != 'doctor':
        return jsonify({'message':'only doctor'}), 403
    uid = request.user['user_id']
    appts = Appointment.query.filter_by(doctor_id=uid, status='pending').all()
    out = []
    for a in appts:
        out.append({'id': a.id, 'patient_id': a.patient_id, 'appointment_time': a.appointment_time.isoformat(), 'status': a.status})
    return jsonify(out)

@doctor_bp.route('/appointments/approve', methods=['POST'])
@token_required
def approve():
    if request.user['role'] != 'doctor':
        return jsonify({'message':'only doctor'}), 403
    data = request.json
    appt_id = data.get('appointment_id')
    a = Appointment.query.get(appt_id)
    if not a or a.doctor_id != request.user['user_id']:
        return jsonify({'message':'invalid'}), 400
    a.status = 'approved'
    db.session.commit()
    return jsonify({'message':'approved'})

@doctor_bp.route('/prescribe', methods=['POST'])
@token_required
def prescribe():
    if request.user['role'] != 'doctor':
        return jsonify({'message':'only doctor'}), 403
    data = request.form or request.json
    patient_id = data.get('patient_id')
    content = data.get('content')
    file_path = None
    if 'file' in request.files:
        file_path = save_uploaded_file(request.files['file'], current_app.config['UPLOAD_FOLDER'])
    p = Prescription(doctor_id=request.user['user_id'], patient_id=patient_id, content=content, file=file_path)
    db.session.add(p)
    # Optionally create/update Treatment + Bill (simplified)
    db.session.commit()
    return jsonify({'message':'prescribed','id': p.id}), 201
