# utils.py
import os, jwt, datetime
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename

SECRET_KEY_DEFAULT = "change-this-secret"

def make_token(payload, secret):
    return jwt.encode(payload, secret, algorithm="HS256")

def decode_token(token, secret):
    return jwt.decode(token, secret, algorithms=["HS256"])

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth = request.headers.get('Authorization')
            if auth and auth.startswith('Bearer '):
                token = auth.split(' ')[1]
        if not token:
            return jsonify({'message':'Token is missing'}), 401
        try:
            secret = current_app.config.get('SECRET_KEY', SECRET_KEY_DEFAULT)
            data = decode_token(token, secret)
            request.user = data  # attach user info (id, role)
        except Exception as e:
            return jsonify({'message':'Token is invalid', 'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated

def save_uploaded_file(fileobj, upload_folder):
    if not fileobj:
        return None
    filename = secure_filename(fileobj.filename)
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, filename)
    fileobj.save(path)
    return path
