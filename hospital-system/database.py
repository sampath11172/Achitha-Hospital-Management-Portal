import sqlite3
from datetime import datetime

DB_NAME = "hospital.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            department TEXT
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_uid TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            diagnosis TEXT,
            history TEXT,
            prescriptions TEXT,
            insurance_status TEXT,
            risk_score INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_uid TEXT NOT NULL,
            doctor TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS beds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ward TEXT NOT NULL,
            bed_code TEXT UNIQUE NOT NULL,
            bed_type TEXT NOT NULL,
            occupied INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry_date TEXT NOT NULL,
            threshold INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS lab_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_uid TEXT NOT NULL,
            test_name TEXT NOT NULL,
            status TEXT NOT NULL,
            report_text TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_uid TEXT NOT NULL,
            treatment_cost REAL NOT NULL,
            medicine_cost REAL NOT NULL,
            room_cost REAL NOT NULL,
            insurance_approved INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS emergency_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_uid TEXT,
            case_notes TEXT NOT NULL,
            severity INTEGER NOT NULL,
            priority_tag TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    _seed_data(conn)
    conn.close()


def _seed_data(conn):
    cur = conn.cursor()
    user_count = cur.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
    if user_count == 0:
        users = [
            ("admin", "admin", "Admin", "System Administrator", "Operations"),
            ("drsmith", "doctor", "Doctor", "Dr. Sarah Smith", "Cardiology"),
            ("nurseamy", "nurse", "Nurse", "Nurse Amy James", "ICU"),
            ("johnp", "patient", "Patient", "John Parker", ""),
        ]
        cur.executemany(
            "INSERT INTO users (username, password_hash, role, full_name, department) VALUES (?, ?, ?, ?, ?)",
            users,
        )

    patient_count = cur.execute("SELECT COUNT(*) c FROM patients").fetchone()["c"]
    if patient_count == 0:
        patients = [
            ("P-2026-001", "John Parker", 52, "Male", "Hypertension", "Diabetes Type II", "Metformin", "Validated", 72),
            ("P-2026-002", "Lina George", 33, "Female", "Asthma", "Allergy", "Inhaler", "Pending", 45),
            ("P-2026-003", "Sam Roy", 67, "Male", "Cardiac Arrhythmia", "Smoker", "Beta blockers", "Validated", 88),
        ]
        cur.executemany(
            """
            INSERT INTO patients (patient_uid, full_name, age, gender, diagnosis, history, prescriptions, insurance_status, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            patients,
        )

    if cur.execute("SELECT COUNT(*) c FROM appointments").fetchone()["c"] == 0:
        appts = [
            ("P-2026-001", "Dr. Sarah Smith", "2026-03-01 09:00", "Approved", "Follow-up"),
            ("P-2026-002", "Dr. Sarah Smith", "2026-03-01 11:30", "Pending", "Initial consult"),
            ("P-2026-003", "Dr. Sarah Smith", "2026-03-02 14:00", "Cancelled", "Reschedule"),
        ]
        cur.executemany(
            "INSERT INTO appointments (patient_uid, doctor, appointment_date, status, notes) VALUES (?, ?, ?, ?, ?)",
            appts,
        )

    if cur.execute("SELECT COUNT(*) c FROM beds").fetchone()["c"] == 0:
        beds = [
            ("A", "A-01", "General", 1), ("A", "A-02", "General", 0), ("B", "B-01", "ICU", 1),
            ("B", "B-02", "ICU", 1), ("C", "C-01", "General", 0),
        ]
        cur.executemany("INSERT INTO beds (ward, bed_code, bed_type, occupied) VALUES (?, ?, ?, ?)", beds)

    if cur.execute("SELECT COUNT(*) c FROM inventory").fetchone()["c"] == 0:
        meds = [
            ("Paracetamol", 250, "2027-01-01", 100),
            ("Insulin", 40, "2026-05-01", 80),
            ("Amoxicillin", 90, "2026-10-21", 75),
        ]
        cur.executemany(
            "INSERT INTO inventory (medicine_name, quantity, expiry_date, threshold) VALUES (?, ?, ?, ?)", meds
        )

    if cur.execute("SELECT COUNT(*) c FROM lab_reports").fetchone()["c"] == 0:
        reports = [
            ("P-2026-001", "Lipid Profile", "Completed", "Elevated LDL", datetime.utcnow().isoformat()),
            ("P-2026-002", "CBC", "Processing", "", datetime.utcnow().isoformat()),
        ]
        cur.executemany(
            "INSERT INTO lab_reports (patient_uid, test_name, status, report_text, created_at) VALUES (?, ?, ?, ?, ?)", reports
        )

    if cur.execute("SELECT COUNT(*) c FROM bills").fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO bills (patient_uid, treatment_cost, medicine_cost, room_cost, insurance_approved, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("P-2026-001", 850.0, 120.0, 400.0, 1, datetime.utcnow().isoformat()),
        )

    if cur.execute("SELECT COUNT(*) c FROM emergency_cases").fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO emergency_cases (patient_uid, case_notes, severity, priority_tag, created_at) VALUES (?, ?, ?, ?, ?)",
            ("P-2026-003", "Chest pain and dizziness", 9, "Critical", datetime.utcnow().isoformat()),
        )

    conn.commit()


def fetch_all(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()
