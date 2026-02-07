# System Architecture and Database Design

## Application Layers
1. **Presentation Layer**: Django templates per role (`admin`, `doctor`, `patient`, `caretaker`).
2. **Business Layer**: Django views + forms implementing RBAC and workflows.
3. **Data Layer**: Django ORM models persisted to PostgreSQL.
4. **Security & Audit Layer**:
   - Django authentication + hashed passwords
   - role-based decorators
   - middleware + signals for audit events

## Core Entities
- `User` (custom auth entity with role)
- `Patient`, `Doctor`, `Caretaker`, `Department`
- `Appointment`, `MedicalRecord`, `Prescription`, `LabReport`
- `Invoice`, `Payment`
- `AuditLog`

## Audit Coverage
- Login events via `user_logged_in` signal.
- Record mutations for medical records, prescriptions, lab reports.
- Appointment changes.
- Billing and payment changes.

## Constraints and Clinical Scope
- The platform **does not** generate automated diagnosis or treatment recommendations.
- Doctors are the source of clinical data creation/updates.
- Patients/caretakers access data in read-oriented flows according to role permissions.
