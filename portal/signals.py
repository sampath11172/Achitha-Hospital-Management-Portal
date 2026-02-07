from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .middleware import get_current_ip
from .models import Appointment, AuditLog, Invoice, LabReport, MedicalRecord, Payment, Prescription


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGIN,
        target_model='User',
        target_id=str(user.id),
        message=f'User {user.username} logged in',
        ip_address=request.META.get('REMOTE_ADDR'),
    )


def _log_change(instance, created, action, message):
    AuditLog.objects.create(
        user=None,
        action=action,
        target_model=instance.__class__.__name__,
        target_id=str(instance.pk),
        message=message,
        ip_address=get_current_ip(),
    )


@receiver(post_save, sender=MedicalRecord)
def log_medical_record(sender, instance, created, **kwargs):
    _log_change(instance, created, AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE, 'Medical record changed')


@receiver(post_save, sender=Prescription)
def log_prescription(sender, instance, created, **kwargs):
    _log_change(instance, created, AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE, 'Prescription changed')


@receiver(post_save, sender=LabReport)
def log_lab_report(sender, instance, created, **kwargs):
    _log_change(instance, created, AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE, 'Lab report changed')


@receiver(post_save, sender=Appointment)
def log_appointment(sender, instance, created, **kwargs):
    _log_change(instance, created, AuditLog.Action.APPOINTMENT, 'Appointment changed')


@receiver(post_save, sender=Invoice)
def log_invoice(sender, instance, created, **kwargs):
    _log_change(instance, created, AuditLog.Action.BILLING, 'Invoice changed')


@receiver(post_save, sender=Payment)
def log_payment(sender, instance, created, **kwargs):
    _log_change(instance, created, AuditLog.Action.BILLING, 'Payment changed')
