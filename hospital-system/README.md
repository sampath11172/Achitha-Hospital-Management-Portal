# Smart Hospital Management System (SHMS)

Pure HTML + CSS + Core Python implementation using `http.server` and SQLite.

## Run
```bash
cd hospital-system
python3 server.py
```

Open: http://localhost:8000

## Deliverables Included
- Web dashboards: Admin, Doctor, Nurse, Patient (desktop/tablet responsive)
- Workflow diagram section
- Feature overview section
- Technical architecture infographic section
- Role-based login and routing
- Patient EHR registration, appointment booking, inventory, lab, billing, ICU tables
- Rule-based AI engine (`ai_engine.py`) with risk, triage, drug checks, restock logic
- SQLite database schema and seed data (`database.py`)

## Source Structure
```text
/hospital-system
├── /templates
│   ├── index.html
│   ├── admin.html
│   ├── doctor.html
│   ├── nurse.html
│   └── patient.html
├── /static
│   ├── style.css
│   └── assets/
├── database.py
├── ai_engine.py
├── auth.py
├── server.py
└── utils.py
```
