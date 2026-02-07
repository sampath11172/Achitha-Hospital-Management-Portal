from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Appointment, Invoice, LabReport, MedicalRecord, Payment, Prescription, User


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=[(User.Role.PATIENT, 'Patient'), (User.Role.CARETAKER, 'Caretaker')])

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role')


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'scheduled_at', 'notes']


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['patient', 'diagnosis_notes']


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medical_record', 'medicines', 'dosage_instructions']


class LabReportForm(forms.ModelForm):
    class Meta:
        model = LabReport
        fields = ['patient', 'test_name', 'request_notes', 'result_notes', 'status']


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'amount', 'description', 'due_date']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice', 'amount', 'method', 'status']
