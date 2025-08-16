# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage
users = {"patient": [], "doctor": [], "staff": []}   # each user is a dict
appointments = []   # each appointment: {patient_name, patient_email, doctor_name, doctor_email, date, time, approved (bool), notified (bool), removed (bool)}
treatments = []     # {patient_email, doctor_email, prescription, days_to_cure, medicines, created_at}
bills = []          # {patient_name, patient_email, doctor_name, doctor_email, fees, medicines, total, paid (bool), created_at}

# Helper to find user
def find_user(role, email):
    for u in users.get(role, []):
        if u.get("email") == email:
            return u
    return None

@app.route("/")
def home():
    return jsonify({"message": "Hospital Management Backend Running"})

# Registration - stores role-specific fields; expects JSON
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    role = data.get("role")
    if role not in users:
        return jsonify({"error":"Invalid role"}), 400
    # required fields: name, email, password; others optional (address, photo_base64, specialization, doj, qualification)
    if not data.get("email") or not data.get("name") or not data.get("password"):
        return jsonify({"error":"name, email and password required"}), 400
    if find_user(role, data["email"]):
        return jsonify({"error":"Email already registered"}), 400
    users[role].append(data)
    return jsonify({"message": f"{role} registered", "user": data}), 201

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    role = data.get("role")
    if role not in users:
        return jsonify({"error":"Invalid role"}), 400
    user = find_user(role, data.get("email"))
    if not user or user.get("password") != data.get("password"):
        return jsonify({"error":"Invalid credentials"}), 401
    return jsonify({"message":"Login successful", "user": user})

# GET lists
@app.route("/patients", methods=["GET"])
def get_patients():
    return jsonify(users["patient"])

@app.route("/doctors", methods=["GET"])
def get_doctors():
    return jsonify(users["doctor"])

@app.route("/staffs", methods=["GET"])
def get_staffs():
    return jsonify(users["staff"])

# Create appointment (patient or staff can create). appointment starts approved=False
@app.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json or {}
    required = ["patient_name","patient_email","doctor_name","doctor_email","date","time"]
    if not all(k in data for k in required):
        return jsonify({"error":"Missing appointment fields"}), 400
    appt = {
        "patient_name": data["patient_name"],
        "patient_email": data["patient_email"],
        "doctor_name": data["doctor_name"],
        "doctor_email": data["doctor_email"],
        "date": data["date"],
        "time": data["time"],
        "approved": False,
        "notified": True,   # staff/doctor will see notification red until toggled by staff
        "removed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    appointments.append(appt)
    return jsonify({"message":"Appointment created", "appointment": appt}), 201

# Get appointments (all)
@app.route("/appointments", methods=["GET"])
def list_appointments():
    return jsonify(appointments)

# Doctor approves appointment (moves it to approved True). endpoint: /appointments/approve with JSON {index}
@app.route("/appointments/approve", methods=["POST"])
def approve_appointment():
    data = request.json or {}
    idx = data.get("index")
    if idx is None or not (0 <= idx < len(appointments)):
        return jsonify({"error":"Invalid index"}), 400
    appointments[idx]["approved"] = True
    # when doctor approves, it's still notified until staff turns it off after meeting
    return jsonify({"message":"Appointment approved", "appointment": appointments[idx]})

# Staff can remove appointment after patient didn't meet (set removed True)
@app.route("/appointments/remove", methods=["POST"])
def remove_appointment():
    data = request.json or {}
    idx = data.get("index")
    if idx is None or not (0 <= idx < len(appointments)):
        return jsonify({"error":"Invalid index"}), 400
    appointments[idx]["removed"] = True
    return jsonify({"message":"Appointment removed", "appointment": appointments[idx]})

# Staff can toggle notification off (after meeting)
@app.route("/appointments/toggle_notify", methods=["POST"])
def toggle_notify():
    data = request.json or {}
    idx = data.get("index")
    if idx is None or not (0 <= idx < len(appointments)):
        return jsonify({"error":"Invalid index"}), 400
    appointments[idx]["notified"] = False
    return jsonify({"message":"Notification turned off", "appointment": appointments[idx]})

# Create treatment/prescription by doctor - stored in treatments and also can update "patient treated" stats
@app.route("/treatments", methods=["POST"])
def create_treatment():
    data = request.json or {}
    required = ["patient_email","doctor_email","prescription","days_to_cure","medicines"]
    if not all(k in data for k in required):
        return jsonify({"error":"Missing treatment fields"}), 400
    t = {
        "patient_email": data["patient_email"],
        "doctor_email": data["doctor_email"],
        "prescription": data["prescription"],
        "days_to_cure": int(data["days_to_cure"]),
        "medicines": data["medicines"],
        "created_at": datetime.utcnow().isoformat()
    }
    treatments.append(t)
    return jsonify({"message":"Treatment added","treatment":t}), 201

@app.route("/treatments", methods=["GET"])
def list_treatments():
    return jsonify(treatments)

# Bills
@app.route("/bills", methods=["POST"])
def create_bill():
    data = request.json or {}
    required = ["patient_name","patient_email","doctor_name","doctor_email","fees","medicines"]
    if not all(k in data for k in required):
        return jsonify({"error":"Missing bill fields"}), 400
    total = float(data.get("fees",0)) + float(data.get("medicines",0))
    b = {
        "patient_name": data["patient_name"],
        "patient_email": data["patient_email"],
        "doctor_name": data["doctor_name"],
        "doctor_email": data["doctor_email"],
        "fees": data["fees"],
        "medicines": data["medicines"],
        "total": total,
        "paid": False,
        "created_at": datetime.utcnow().isoformat()
    }
    bills.append(b)
    return jsonify({"message":"Bill created","bill":b}), 201

@app.route("/bills", methods=["GET"])
def list_bills():
    return jsonify(bills)

@app.route("/bills/pay", methods=["POST"])
def pay_bill():
    data = request.json or {}
    idx = data.get("index")
    if idx is None or not (0 <= idx < len(bills)):
        return jsonify({"error":"Invalid index"}), 400
    bills[idx]["paid"] = True
    bills[idx]["paid_at"] = datetime.utcnow().isoformat()
    return jsonify({"message":"Bill paid","bill":bills[idx]})

# PDF downloads
@app.route("/download_appointment/<int:idx>", methods=["GET"])
def download_appointment(idx):
    if idx < 0 or idx >= len(appointments):
        return jsonify({"error":"Appointment not found"}), 404
    appt = appointments[idx]
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(80, 780, "Appointment Letter")
    p.setFont("Helvetica", 12)
    p.drawString(80, 740, f"Patient: {appt['patient_name']}")
    p.drawString(80, 720, f"Patient Email: {appt['patient_email']}")
    p.drawString(80, 700, f"Doctor: {appt['doctor_name']}")
    p.drawString(80, 680, f"Date: {appt['date']}    Time: {appt['time']}")
    p.drawString(80, 660, f"Approved: {'Yes' if appt['approved'] else 'No'}")
    p.showPage()
    p.save()
    buffer.seek(0)
    filename = f"appointment_{idx}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

@app.route("/download_bill/<int:idx>", methods=["GET"])
def download_bill(idx):
    if idx < 0 or idx >= len(bills):
        return jsonify({"error":"Bill not found"}), 404
    bill = bills[idx]
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(80, 780, "Hospital Bill")
    p.setFont("Helvetica", 12)
    p.drawString(80, 740, f"Patient: {bill['patient_name']}")
    p.drawString(80, 720, f"Doctor: {bill['doctor_name']}")
    p.drawString(80, 700, f"Fees: {bill['fees']}")
    p.drawString(80, 680, f"Medicines: {bill['medicines']}")
    p.drawString(80, 660, f"Total: {bill['total']}")
    p.drawString(80, 640, f"Paid: {'Yes' if bill.get('paid') else 'No'}")
    p.showPage()
    p.save()
    buffer.seek(0)
    filename = f"bill_{idx}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
