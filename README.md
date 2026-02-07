# Hospital Management Portal

A secure, role-based Hospital Management Portal built with Django Templates, Django ORM, and PostgreSQL support.

## Tech Stack
- Frontend: HTML/CSS/JavaScript (Django templates)
- Backend: Django
- Database: PostgreSQL (`django.db.backends.postgresql` when `POSTGRES_DB` is set)

## Role-Based Access
- **Admin**: user management, billing controls, audit log visibility.
- **Doctor**: appointments, medical records, prescriptions, lab request/result entry.
- **Patient**: registration/login, appointment booking, prescriptions, reports, invoices/payments view.
- **Caretaker**: linked patient visibility for appointments, prescriptions, labs, billing.

## Security Measures
- Custom `User` model with explicit role field.
- Django password hashing and authentication.
- RBAC enforced by role checks (`role_required`) plus login checks.
- CSRF middleware active for all form posts.
- HTTP-only session and CSRF cookies configured.
- Audit logging for login, records, appointments, billing, and payments.

## Quick Start
1. Create virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure PostgreSQL environment variables:
   ```bash
   export POSTGRES_DB=hospital
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD=postgres
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   ```
3. Run migrations and server:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

## Project Structure
- `hospital_portal/`: project settings and root URLs
- `portal/models.py`: database entities and relationships
- `portal/views.py`: role-specific dashboards and actions
- `portal/signals.py`: audit event generation
- `portal/templates/`: Django template UI by role
- `docs/architecture.md`: architecture and DB design notes
