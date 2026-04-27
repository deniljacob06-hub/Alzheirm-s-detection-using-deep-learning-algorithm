"""
URL configuration for medico project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from medico_app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('users-login/',views.users_login),
    #admin
    path('admin-dashboard/',views.admin_dashboard),
    path('admin-approvehospital/',views.admin_approvehospital),
    path('admin-approvesinglehospital/',views.admin_approvesinglehospital),
    path('admin-viewhospitals/',views.admin_viewhospitals),
    path('admin-rejectsinglehospital/',views.admin_rejectsinglehospital),
    path('admin-viewdoctors/',views.admin_viewdoctors),
    path('admin-adddepartments/',views.admin_adddepartments),
    path('admin-updatedepartment/',views.admin_updatedepartment),
    path('admin-deletedepartment/',views.admin_deletedepartment),
    path('admin-viewappointments/',views.admin_viewappointments),
    path('admin-viewmedicalrecord/',views.admin_viewmedicalrecord),
    #hospital
    path('hospital-signup/',views.hospital_signup),
    path('hospital-dashboard/',views.hospital_dashboard),
    path('hospital-adddoctor/',views.hospital_adddoctor),
    path('hospital-viewdoctors/',views.hospital_viewdoctors),
    path('hospital-viewdocappointments/',views.hospital_viewdocappointments),
    path('hospital-viewmedicalrecord/',views.hospital_viewmedicalrecord),
    path('hospital-viewprofile/',views.hospital_viewprofile),
    path('hospital-updateprofile/',views.hospital_updateprofile),
    #patient
    path('patient-signup/',views.patient_signup),
    path('patient-dashboard/',views.patient_dashboard),
    path('patient-viewhospitals/',views.patient_viewhospitals),
    path('patient-viewdoctors/',views.patient_viewdoctors),
    path('patient-makeappointment/',views.patient_makeappointment),
    path('patient-viewappointments/',views.patient_viewappointments),
    path('patient-cancelappointment/',views.patient_cancelappointment),
    path('patient-payfeeappointment/',views.patient_payfeeappointment),
    path('patient-addcarddetails/',views.patient_addcarddetails),
    path('patient-viewprescription/',views.patient_viewprescription),
    path('patient-viewmedicalrecord/',views.patient_viewmedicalrecord),
    path('Uploadimage/',views.Uploadimage),
    path('Uploadimages/',views.Uploadimages),
    # path('patient-viewprofile/',views.patient_viewprofile),
    #doctor
    path('doctor-dashboard/',views.doctor_dashboard),
    path('doctor-viewappointments/',views.doctor_viewappointments),
    path('doctor-approveappointment/',views.doctor_approveappointment),
    path('doctor-rejectappointment/',views.doctor_rejectappointment),
    path('doctor-markstatus/',views.doctor_markstatus),
    path('doctor-addmedical/',views.doctor_addmedical),
    path('doctor-viewmedicalrecord/',views.doctor_viewmedicalrecord),

    path('bot/',views.bot),
]
