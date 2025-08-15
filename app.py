from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from reportlab.pdfgen import canvas
import base64

app = Flask(__name__)
CORS(app)

users = {"patient": [], "doctor": [], "staff": []}
appointments = []
treatments = []
bills = []

@app.route("/")
def home():
    return jsonify({"message": "Hospital Management Backend Running"})

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    role = data.get("role")
    if role not in users:
        return jsonify({"error": "Invalid role"}), 400
    users[role].append(data)
    return jsonify({"message": f"{role.capitalize()} registered successfully", "data": data})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role = data.get("role")
    for user in users.get(role, []):
        if user["email"] == data["email"] and user["password"] == data["password"]:
            return jsonify({"message": "Login successful", "user": user})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/patients", methods=["GET"])
def get_patients():
    return jsonify(users["patient"])

@app.route("/doctors", methods=["GET"])
def get_doctors():
    return jsonify(users["doctor"])

@app.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json
    appointments.append(data)
    return jsonify({"message": "Appointment created", "appointment": data})

@app.route("/appointments", methods=["GET"])
def get_appointments():
    return jsonify(appointments)

@app.route("/treatments", methods=["POST"])
def create_treatment():
    data = request.json
    treatments.append(data)
    return jsonify({"message": "Treatment added", "treatment": data})

@app.route("/treatments", methods=["GET"])
def get_treatments():
    return jsonify(treatments)

@app.route("/bills", methods=["POST"])
def create_bill():
    data = request.json
    bills.append(data)
    return jsonify({"message": "Bill generated", "bill": data})

@app.route("/bills", methods=["GET"])
def get_bills():
    return jsonify(bills)

@app.route("/download_bill/<int:bill_id>", methods=["GET"])
def download_bill(bill_id):
    if bill_id >= len(bills):
        return jsonify({"error": "Bill not found"}), 404

    bill = bills[bill_id]
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 14)
    p.drawString(100, 750, f"Hospital Bill - {bill['patient_name']}")
    p.drawString(100, 730, f"Doctor: {bill['doctor_name']}")
    p.drawString(100, 710, f"Fees: {bill['fees']}")
    p.drawString(100, 690, f"Medicines: {bill['medicines']}")
    p.drawString(100, 670, f"Total: {bill['total']}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="bill.pdf", mimetype="application/pdf")

@app.route("/download_appointment/<int:appt_id>", methods=["GET"])
def download_appointment(appt_id):
    if appt_id >= len(appointments):
        return jsonify({"error": "Appointment not found"}), 404

    appt = appointments[appt_id]
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 14)
    p.drawString(100, 750, "Appointment Letter")
    p.drawString(100, 730, f"Patient: {appt['patient_name']}")
    p.drawString(100, 710, f"Doctor: {appt['doctor_name']}")
    p.drawString(100, 690, f"Date: {appt['date']}")
    p.drawString(100, 670, f"Time: {appt['time']}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="appointment.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
