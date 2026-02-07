from django.contrib import admin

from .models import (
    Appointment,
    AuditLog,
    Caretaker,
    Department,
    Doctor,
    Invoice,
    LabReport,
    MedicalRecord,
    Patient,
    Payment,
    Prescription,
    User,
)

admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Caretaker)
admin.site.register(Department)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(Prescription)
admin.site.register(LabReport)
admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(AuditLog)
