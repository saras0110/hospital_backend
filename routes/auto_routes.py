# routes/auth_routes.py
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, Patient, Doctor, Staff
from utils import make_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.form or request.json
    role = data.get('role')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    if not (role and email and password):
        return jsonify({'message':'role, email, password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message':'Email already exists'}), 400

    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash, role=role, name=name)
    # Save photo if provided
    photo = None
    if 'photo' in request.files:
        from utils import save_uploaded_file
        photo = save_uploaded_file(request.files['photo'], current_app.config['UPLOAD_FOLDER'])
        user.photo = photo

    db.session.add(user)
    db.session.commit()

    # create role-specific row
    if role == 'patient':
        p = Patient(id=user.id,
                    address=data.get('address'),
                    age=int(data.get('age')) if data.get('age') else None,
                    gender=data.get('gender'),
                    contact=data.get('contact'))
        db.session.add(p)
    elif role == 'doctor':
        d = Doctor(id=user.id,
                   specialization=data.get('specialization'),
                   qualification=data.get('qualification'))
        db.session.add(d)
    elif role == 'staff':
        s = Staff(id=user.id, qualification=data.get('qualification'))
        db.session.add(s)

    db.session.commit()
    return jsonify({'message':'registered','user_id': user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not (email and password):
        return jsonify({'message':'email and password required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message':'Invalid credentials'}), 401
    payload = {'user_id': user.id, 'role': user.role, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}
    token = make_token(payload, current_app.config.get('SECRET_KEY'))
    return jsonify({'token': token, 'role': user.role, 'user_id': user.id})
