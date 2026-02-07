from django.conf import settings
from django.db import migrations, models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('DOCTOR', 'Doctor'), ('PATIENT', 'Patient'), ('CARETAKER', 'Caretaker')], max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={'abstract': False},
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialization', models.CharField(max_length=255)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='portal.department')),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='doctor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField()),
                ('blood_group', models.CharField(max_length=5)),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='patient_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnosis_notes', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='medical_records', to='portal.doctor')),
                ('patient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='medical_records', to='portal.patient')),
            ],
        ),
        migrations.CreateModel(
            name='LabReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=255)),
                ('request_notes', models.TextField()),
                ('result_notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('REQUESTED', 'Requested'), ('COMPLETED', 'Completed')], default='REQUESTED', max_length=20)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='lab_reports', to='portal.doctor')),
                ('patient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='lab_reports', to='portal.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateField()),
                ('patient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='invoices', to='portal.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Caretaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patients', models.ManyToManyField(blank=True, related_name='caretakers', to='portal.patient')),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='caretaker_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('LOGIN', 'User login'), ('CREATE', 'Record create'), ('UPDATE', 'Record update'), ('APPOINTMENT', 'Appointment change'), ('BILLING', 'Billing/Payment change')], max_length=20)),
                ('target_model', models.CharField(max_length=100)),
                ('target_id', models.CharField(blank=True, max_length=50)),
                ('message', models.TextField()),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('BOOKED', 'Booked'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='BOOKED', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='appointments', to='portal.doctor')),
                ('patient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='appointments', to='portal.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicines', models.TextField()),
                ('dosage_instructions', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='prescriptions', to='portal.doctor')),
                ('medical_record', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='prescriptions', to='portal.medicalrecord')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid')], default='PAID', max_length=20)),
                ('paid_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('invoice', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='payments', to='portal.invoice')),
            ],
        ),
    ]
