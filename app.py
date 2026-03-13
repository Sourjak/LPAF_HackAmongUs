from flask import Flask, render_template, request, redirect, send_file, jsonify
import uuid
import ipaddress
import sqlite3
import time
import os

# Custom utility imports
from utils.qr_generator import generate_qr_code
from utils.token_manager import generate_session_token, verify_session_token
from utils.validator import is_ip_allowed
from utils.report_generator import generate_report

app = Flask(__name__)

# -------------------------
# Step 1: Configuration & Database Pathing
# -------------------------
app.config["SECRET_KEY"] = "lpaf_super_secret_key"

# Establish Absolute Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")

def init_db():
    """Ensures the local SQLite database directory and table are ready with Device ID migration."""
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    
    # Using check_same_thread=False for SQLite concurrency
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        name TEXT,
        roll TEXT,
        ip TEXT,
        device_id TEXT
    )
    """)

    # SCHEMA MIGRATION: Ensure device_id column exists
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [col[1] for col in cursor.fetchall()]

    if "device_id" not in columns:
        cursor.execute("ALTER TABLE attendance ADD COLUMN device_id TEXT")

    conn.commit()
    conn.close()

# Initialize DB and session tracker
init_db()
active_sessions = {}

# -------------------------
# Step 2: Homepage Route
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# Step 3: Professor Dashboard (Session Creation)
# -------------------------
@app.route("/professor", methods=["GET", "POST"])
def professor():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        section = request.form.get("section", "").strip()
        department = request.form.get("department", "").strip()
        
        # Capture Dynamic Duration (Default 300s)
        try:
            duration = int(request.form.get("duration", 300))
        except (ValueError, TypeError):
            duration = 300

        if not email or not subject or not section or not department:
            return "All fields must be filled before generating QR.", 400

        session_id = str(uuid.uuid4())[:8]

        professor_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        professor_ip = professor_ip.split(",")[0].strip()
        
        network = ipaddress.ip_network(professor_ip + "/24", strict=False)
        allowed_network = str(network)

        token = generate_session_token(session_id)
        student_link = request.host_url + f"student?token={token}"
        qr_image = generate_qr_code(student_link)

        session_data = {
            "email": email,
            "subject": subject,
            "section": section,
            "department": department,
            "professor_ip": professor_ip,
            "allowed_network": allowed_network,
            "token": token,
            "start_time": time.time(),
            "duration": duration 
        }
        active_sessions[session_id] = session_data

        return render_template(
            "professor.html",
             qr_image=qr_image,
             session_id=session_id,
             token=token,
             start_time=session_data["start_time"],
             duration=session_data["duration"]
       )
            
    return render_template("professor.html")

# -------------------------
# Step 4: API Endpoints (QR Refresh, Stats, & Reports)
# -------------------------
@app.route("/refresh_qr/<session_id>")
def refresh_qr(session_id):
    if session_id not in active_sessions:
        return jsonify({"error": "Invalid session"}), 404

    session = active_sessions[session_id]

    # Expiry Logic: Auto-send report and end session
    if time.time() - session["start_time"] > session["duration"]:
        report_path = generate_report(
            session_id,
            session["section"],
            session["subject"],
            session["department"],
            session["email"]
        )
        print("Session expired. Report generated:", report_path)
        active_sessions.pop(session_id, None)
        return jsonify({"expired": True})

    token = generate_session_token(session_id)
    session["token"] = token

    student_link = request.host_url + f"student?token={token}"
    qr_image = generate_qr_code(student_link)

    return jsonify({
        "qr": qr_image,
        "token": token
    })

@app.route("/end_session/<session_id>")
def end_session(session_id):
    session = active_sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Generate report
    report_path = generate_report(
        session_id,
        session["section"],
        session["subject"],
        session["department"],
        session["email"]
    )

    # Send email
    print("Session ended. Report generated:", report_path)

    # Remove session
    active_sessions.pop(session_id, None)
    return jsonify({"status": "Session ended and report emailed"})

@app.route("/session_stats/<session_id>")
def session_stats(session_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT name, roll FROM attendance WHERE session_id=?", (session_id,))
    rows = cursor.fetchall()
    conn.close()

    return jsonify({
        "count": len(rows),
        "recent": rows[-5:] 
    })

@app.route("/download_report/<session_id>")
def download_report(session_id):
    session = active_sessions.get(session_id)
    if not session:
        return "Session expired but report can still be generated via database admin.", 404

    file_path = generate_report(
        session_id,
        session["section"],
        session["subject"],
        session["department"],
        session["email"]
    )

    if not file_path:
        return "No records available for download.", 404
    
    return send_file(file_path, as_attachment=True)

# -------------------------
# Step 5: Student Verification & Submission
# -------------------------
@app.route("/student")
def student():
    token = request.args.get("token")

    if not token:
        return "Invalid QR Code - Missing Token", 400

    decoded = verify_session_token(token)

    if not decoded:
        return "The QR link has expired or is invalid.", 401

    session_id = decoded["session_id"]
    session = active_sessions.get(session_id)

    if not session:
        return "Session expired.", 400

    # Calculate remaining time for the student's countdown
    expiry_time = int(session["start_time"] + session["duration"] - time.time())

    return render_template(
        "student.html",
        token=token,
        session_id=session_id,
        expiry_time=expiry_time,
        location=session["allowed_network"]
    )

@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    name = request.form.get("name", "").strip()
    roll = request.form.get("roll", "").strip().upper()
    token = request.form.get("token")
    device_id = request.form.get("device_id", "").strip()

    if not token:
        return "Invalid request - Missing verification token.", 400

    if not name or not roll:
        return "Name and Roll number are required.", 400
    
    if not device_id:
        return "Device verification failed. Please refresh the page.", 400

    decoded = verify_session_token(token)
    if not decoded:
        return "Session has expired.", 401

    session_id = decoded["session_id"]
    
    student_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    student_ip = student_ip.split(",")[0].strip()

    session = active_sessions.get(session_id)
    if not session:
        return "This attendance session is no longer active.", 400

    allowed_network = session["allowed_network"]
    if not is_ip_allowed(student_ip, allowed_network):
        return "You must be connected to the campus network to mark attendance.", 403

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM attendance WHERE session_id=? AND (roll=? OR device_id=?)",
        (session_id, roll, device_id)
    )

    if cursor.fetchone():
        conn.close()
        return "Attendance already recorded for this roll number or device.", 409

    cursor.execute(
        "INSERT INTO attendance (session_id, name, roll, ip, device_id) VALUES (?, ?, ?, ?, ?)",
        (session_id, name, roll, student_ip, device_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"redirect": f"/success?name={name}&roll={roll}"})

@app.route("/success")
def success():
    name = request.args.get("name", "")
    roll = request.args.get("roll", "")
    return render_template("success.html", name=name, roll=roll)

# -------------------------
# Step 6: Run Server
# -------------------------
if __name__ == "__main__":
    # Dynamically pick the port from environment variables (important for Render/Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
