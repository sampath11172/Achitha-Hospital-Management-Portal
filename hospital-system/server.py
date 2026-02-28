import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from ai_engine import (
    inventory_restock_alert,
    patient_risk_score,
    reminder_schedule,
    triage_priority,
)
from auth import create_session_token, make_session_cookie, parse_session_token, read_cookie
from database import execute, fetch_all, init_db
from utils import generate_patient_uid

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


class SHMSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/static/"):
            return self.serve_static(parsed.path)

        if parsed.path == "/":
            return self.render_template("index.html", {"message": ""})
        if parsed.path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "session=; Max-Age=0; Path=/")
            self.send_header("Location", "/")
            self.end_headers()
            return

        session = self.get_session()
        if parsed.path == "/admin":
            return self.guard_dashboard(session, "Admin", "admin.html", self.dashboard_context())
        if parsed.path == "/doctor":
            return self.guard_dashboard(session, "Doctor", "doctor.html", self.dashboard_context())
        if parsed.path == "/nurse":
            return self.guard_dashboard(session, "Nurse", "nurse.html", self.dashboard_context())
        if parsed.path == "/patient":
            return self.guard_dashboard(session, "Patient", "patient.html", self.dashboard_context())

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = {k: v[0] for k, v in parse_qs(body).items()}

        if parsed.path == "/login":
            username = data.get("username", "")
            password = data.get("password", "")
            rows = fetch_all(
                "SELECT username, password_hash, role FROM users WHERE username=?", (username,)
            )
            if rows and rows[0]["password_hash"] == password:
                token = create_session_token(rows[0]["username"], rows[0]["role"])
                self.send_response(302)
                self.send_header("Set-Cookie", make_session_cookie(token))
                destination = "/" + rows[0]["role"].lower()
                self.send_header("Location", destination)
                self.end_headers()
                return
            return self.render_template("index.html", {"message": "Invalid credentials"})

        session = self.get_session()
        if not session:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        if parsed.path == "/register-patient" and session["role"] in ["Admin", "Nurse"]:
            count = fetch_all("SELECT COUNT(*) c FROM patients")[0]["c"] + 1
            pid = generate_patient_uid(count)
            diagnosis = data.get("diagnosis", "")
            history = data.get("history", "")
            score = patient_risk_score(int(data.get("age", 0)), diagnosis, history)
            execute(
                """
                INSERT INTO patients (patient_uid, full_name, age, gender, diagnosis, history, prescriptions, insurance_status, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    data.get("full_name"),
                    int(data.get("age", 0)),
                    data.get("gender", "Unknown"),
                    diagnosis,
                    history,
                    data.get("prescriptions", ""),
                    data.get("insurance_status", "Pending"),
                    score,
                ),
            )
            self.send_response(302)
            self.send_header("Location", "/admin")
            self.end_headers()
            return

        if parsed.path == "/book-appointment" and session["role"] in ["Patient", "Admin"]:
            execute(
                "INSERT INTO appointments (patient_uid, doctor, appointment_date, status, notes) VALUES (?, ?, ?, ?, ?)",
                (
                    data.get("patient_uid", "P-Unknown"),
                    data.get("doctor", "Dr. Sarah Smith"),
                    data.get("appointment_date", ""),
                    "Pending",
                    data.get("notes", "Telemedicine"),
                ),
            )
            self.send_response(302)
            self.send_header("Location", "/patient")
            self.end_headers()
            return

        self.send_error(403, "Forbidden")

    def guard_dashboard(self, session, role, template, context):
        if not session or session["role"] != role:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return
        return self.render_template(template, context)

    def get_session(self):
        token = read_cookie(self.headers.get("Cookie"), "session")
        if not token:
            return None
        return parse_session_token(token)

    def dashboard_context(self):
        patients = fetch_all("SELECT * FROM patients")
        beds = fetch_all("SELECT * FROM beds")
        appointments = fetch_all("SELECT * FROM appointments ORDER BY appointment_date LIMIT 10")
        inventory = fetch_all("SELECT * FROM inventory")
        lab_reports = fetch_all("SELECT * FROM lab_reports ORDER BY created_at DESC LIMIT 6")
        emergency = fetch_all("SELECT * FROM emergency_cases ORDER BY created_at DESC LIMIT 6")
        bills = fetch_all("SELECT * FROM bills ORDER BY created_at DESC LIMIT 10")

        occupied = sum(1 for b in beds if b["occupied"])
        bed_rate = int((occupied / len(beds)) * 100) if beds else 0
        revenue = sum((b["treatment_cost"] + b["medicine_cost"] + b["room_cost"]) for b in bills)

        inv_alerts = [
            f"{row['medicine_name']}: {inventory_restock_alert(row['quantity'], row['threshold'], row['expiry_date'])}"
            for row in inventory
        ]
        triage = triage_priority({"heart_rate": 132, "spo2": 86, "bp_sys": 185})
        reminders = "<br>".join(reminder_schedule("2026-03-01 09:00"))

        return {
            "total_patients": str(len(patients)),
            "bed_occupancy": str(bed_rate),
            "monthly_revenue": f"{revenue:.2f}",
            "emergency_alerts": str(len([e for e in emergency if e['severity'] >= 7])),
            "staff_count": str(len(fetch_all("SELECT * FROM users WHERE role IN ('Doctor','Nurse','Admin')"))),
            "patient_rows": "".join(
                f"<tr><td>{p['patient_uid']}</td><td>{p['full_name']}</td><td>{p['diagnosis']}</td><td>{p['risk_score']}</td></tr>"
                for p in patients
            ),
            "appointment_rows": "".join(
                f"<tr><td>{a['patient_uid']}</td><td>{a['doctor']}</td><td>{a['appointment_date']}</td><td>{a['status']}</td></tr>"
                for a in appointments
            ),
            "inventory_rows": "".join(
                f"<tr><td>{i['medicine_name']}</td><td>{i['quantity']}</td><td>{i['expiry_date']}</td><td>{i['threshold']}</td></tr>"
                for i in inventory
            ),
            "lab_rows": "".join(
                f"<tr><td>{l['patient_uid']}</td><td>{l['test_name']}</td><td>{l['status']}</td><td>{l['report_text']}</td></tr>"
                for l in lab_reports
            ),
            "emergency_rows": "".join(
                f"<tr><td>{e['patient_uid']}</td><td>{e['case_notes']}</td><td>{e['severity']}</td><td>{e['priority_tag']}</td></tr>"
                for e in emergency
            ),
            "inventory_alerts": "<br>".join(inv_alerts),
            "triage_level": triage,
            "reminders": reminders,
        }

    def render_template(self, template_name, context):
        path = os.path.join(TEMPLATE_DIR, template_name)
        with open(path, "r", encoding="utf-8") as fh:
            html = fh.read()
        for key, value in context.items():
            html = html.replace("{{" + key + "}}", str(value))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_static(self, path):
        local_path = os.path.join(BASE_DIR, path.lstrip("/"))
        if not os.path.exists(local_path):
            self.send_error(404)
            return
        ext = os.path.splitext(local_path)[1]
        content_type = "text/plain"
        if ext == ".css":
            content_type = "text/css"
        elif ext == ".svg":
            content_type = "image/svg+xml"
        elif ext == ".png":
            content_type = "image/png"

        with open(local_path, "rb") as fh:
            content = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(content)


def run():
    init_db()
    server = ThreadingHTTPServer(("0.0.0.0", 8000), SHMSHandler)
    print("SHMS running at http://localhost:8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
