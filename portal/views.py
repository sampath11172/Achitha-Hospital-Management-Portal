from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import (
    AppointmentForm,
    InvoiceForm,
    LabReportForm,
    MedicalRecordForm,
    PaymentForm,
    PrescriptionForm,
    SignUpForm,
)
from .models import Appointment, AuditLog, Caretaker, Doctor, Invoice, LabReport, MedicalRecord, Patient, Payment, Prescription, User


def home(request):
    return render(request, 'shared/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            user.role = role
            user.save()
            if role == User.Role.PATIENT:
                Patient.objects.create(user=user, date_of_birth='2000-01-01', blood_group='NA')
            elif role == User.Role.CARETAKER:
                Caretaker.objects.create(user=user)
            login(request, user)
            return redirect('role-dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def role_dashboard(request):
    role_map = {
        User.Role.ADMIN: 'admin-dashboard',
        User.Role.DOCTOR: 'doctor-dashboard',
        User.Role.PATIENT: 'patient-dashboard',
        User.Role.CARETAKER: 'caretaker-dashboard',
    }
    return redirect(role_map[request.user.role])


@login_required
@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    context = {
        'users': User.objects.count(),
        'appointments': Appointment.objects.count(),
        'invoices': Invoice.objects.count(),
        'audit_logs': AuditLog.objects.all()[:20],
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@role_required(User.Role.ADMIN)
def admin_billing(request):
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, prefix='invoice')
        payment_form = PaymentForm(request.POST, prefix='payment')
        if invoice_form.is_valid():
            invoice_form.save()
            messages.success(request, 'Invoice created successfully.')
            return redirect('admin-billing')
        if payment_form.is_valid():
            payment_form.save()
            messages.success(request, 'Payment recorded successfully.')
            return redirect('admin-billing')
    else:
        invoice_form = InvoiceForm(prefix='invoice')
        payment_form = PaymentForm(prefix='payment')

    invoices = Invoice.objects.select_related('patient__user').all()
    payments = Payment.objects.select_related('invoice__patient__user').all()
    return render(request, 'admin/billing.html', {
        'invoice_form': invoice_form,
        'payment_form': payment_form,
        'invoices': invoices,
        'payments': payments,
    })


@login_required
@role_required(User.Role.DOCTOR)
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user')
    medical_records = MedicalRecord.objects.filter(doctor=doctor).select_related('patient__user')
    return render(request, 'doctor/dashboard.html', {
        'appointments': appointments,
        'medical_records': medical_records,
    })


@login_required
@role_required(User.Role.DOCTOR)
def doctor_records(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    if request.method == 'POST':
        record_form = MedicalRecordForm(request.POST, prefix='record')
        prescription_form = PrescriptionForm(request.POST, prefix='prescription')
        lab_form = LabReportForm(request.POST, prefix='lab')
        if record_form.is_valid():
            record = record_form.save(commit=False)
            record.doctor = doctor
            record.save()
            messages.success(request, 'Medical record saved.')
            return redirect('doctor-records')
        if prescription_form.is_valid():
            prescription = prescription_form.save(commit=False)
            prescription.doctor = doctor
            prescription.save()
            messages.success(request, 'Prescription saved.')
            return redirect('doctor-records')
        if lab_form.is_valid():
            lab = lab_form.save(commit=False)
            lab.doctor = doctor
            lab.save()
            messages.success(request, 'Lab report saved.')
            return redirect('doctor-records')
    else:
        record_form = MedicalRecordForm(prefix='record')
        prescription_form = PrescriptionForm(prefix='prescription')
        lab_form = LabReportForm(prefix='lab')

    return render(request, 'doctor/records.html', {
        'record_form': record_form,
        'prescription_form': prescription_form,
        'lab_form': lab_form,
        'records': MedicalRecord.objects.filter(doctor=doctor).select_related('patient__user'),
        'labs': LabReport.objects.filter(doctor=doctor).select_related('patient__user'),
    })


@login_required
@role_required(User.Role.PATIENT)
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor__user')
    prescriptions = Prescription.objects.filter(medical_record__patient=patient).select_related('doctor__user')
    labs = LabReport.objects.filter(patient=patient).select_related('doctor__user')
    invoices = Invoice.objects.filter(patient=patient)
    total_paid = Payment.objects.filter(invoice__patient=patient, status=Payment.Status.PAID).aggregate(total=Sum('amount'))['total']

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(request, 'Appointment booked.')
            return redirect('patient-dashboard')
    else:
        form = AppointmentForm()

    return render(request, 'patient/dashboard.html', {
        'appointment_form': form,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'labs': labs,
        'invoices': invoices,
        'total_paid': total_paid or 0,
    })


@login_required
@role_required(User.Role.CARETAKER)
def caretaker_dashboard(request):
    caretaker = get_object_or_404(Caretaker, user=request.user)
    patients = caretaker.patients.select_related('user')
    patient_ids = patients.values_list('id', flat=True)
    context = {
        'patients': patients,
        'appointments': Appointment.objects.filter(patient_id__in=patient_ids).select_related('patient__user', 'doctor__user'),
        'prescriptions': Prescription.objects.filter(medical_record__patient_id__in=patient_ids).select_related('medical_record__patient__user', 'doctor__user'),
        'labs': LabReport.objects.filter(patient_id__in=patient_ids).select_related('patient__user', 'doctor__user'),
        'invoices': Invoice.objects.filter(patient_id__in=patient_ids).select_related('patient__user'),
        'payments': Payment.objects.filter(invoice__patient_id__in=patient_ids).select_related('invoice__patient__user'),
    }
    return render(request, 'caretaker/dashboard.html', context)
