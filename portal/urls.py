from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.role_dashboard, name='role-dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/billing/', views.admin_billing, name='admin-billing'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor-dashboard'),
    path('doctor/records/', views.doctor_records, name='doctor-records'),
    path('patient/dashboard/', views.patient_dashboard, name='patient-dashboard'),
    path('caretaker/dashboard/', views.caretaker_dashboard, name='caretaker-dashboard'),
]
