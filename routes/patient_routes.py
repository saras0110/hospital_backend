# routes/patient_routes.py
from flask import Blueprint, request, jsonify, current_app, send_file
from utils import token_required, save_uploaded_file
from database import db
from models import User, Patient, Doctor, Appointment, Message, Prescription, Bill, Treatment
from datetime import datetime

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/profile', methods=['GET'])
@token_required
def profile():
    uid = request.user['user_id']
    user = User.query.get(uid)
    if not user or user.role != 'patient':
        return jsonify({'message':'Not a patient'}), 403
    patient = user.patient
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'photo': user.photo,
        'address': patient.address,
        'age': patient.age,
        'gender': patient.gender,
        'contact': patient.contact
    })

@patient_bp.route('/doctors', methods=['GET'])
@token_required
def doctors():
    # optional query ?specialization=Cardio
    spec = request.args.get('specialization')
    qs = Doctor.query
    if spec:
        qs = qs.filter(Doctor.specialization.ilike(f'%{spec}%'))
    doctors = qs.all()
    out = []
    for d in doctors:
        out.append({
            'id': d.id,
            'name': d.user.name,
            'specialization': d.specialization,
            'qualification': d.qualification,
            'photo': d.user.photo
        })
    return jsonify(out)

@patient_bp.route('/appointment', methods=['POST'])
@token_required
def book_appointment():
    uid = request.user['user_id']
    if request.user['role'] != 'patient':
        return jsonify({'message':'Only patient can book'}), 403
    data = request.json
    doctor_id = data.get('doctor_id')
    apptime = data.get('appointment_time')  # ISO string
    dt = datetime.fromisoformat(apptime)
    appt = Appointment(patient_id=uid, doctor_id=doctor_id, appointment_time=dt, status='pending')
    db.session.add(appt)
    db.session.commit()
    return jsonify({'message':'appointment requested','appointment_id': appt.id}), 201

@patient_bp.route('/message', methods=['POST'])
@token_required
def message_doctor():
    if request.user['role'] != 'patient':
        return jsonify({'message':'only patient allowed'}), 403
    uid = request.user['user_id']
    data = request.form or request.json
    doctor_id = data.get('doctor_id')
    content = data.get('content')
    image_path = None
    if 'image' in request.files:
        image_path = save_uploaded_file(request.files['image'], current_app.config['UPLOAD_FOLDER'])
    msg = Message(patient_id=uid, doctor_id=doctor_id, content=content, image=image_path)
    db.session.add(msg)
    db.session.commit()
    return jsonify({'message':'sent','id':msg.id}), 201

@patient_bp.route('/treatments', methods=['GET'])
@token_required
def treatments():
    uid = request.user['user_id']
    ts = Treatment.query.filter_by(patient_id=uid).all()
    out = []
    for t in ts:
        out.append({
            'id': t.id,
            'doctor_id': t.doctor_id,
            'start_date': t.start_date.isoformat() if t.start_date else None,
            'days_estimate': t.days_estimate,
            'status': t.status,
            'medicines': t.medicines
        })
    return jsonify(out)

@patient_bp.route('/bills', methods=['GET'])
@token_required
def bills():
    uid = request.user['user_id']
    bills = Bill.query.filter_by(patient_id=uid).all()
    out = []
    for b in bills:
        out.append({'id': b.id, 'amount': b.amount, 'details': b.details, 'paid': b.paid, 'created_at': b.created_at.isoformat()})
    return jsonify(out)
