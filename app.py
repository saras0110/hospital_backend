# app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from database import db, init_db
from models import *
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.staff_routes import staff_bp

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', './static/uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Init
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')

    @app.route('/')
    def ping():
        return jsonify({'status':'ok','message':'Hospital backend running'})

    with app.app_context():
        init_db(app)

    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
