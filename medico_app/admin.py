from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Login)
admin.site.register(HospitalReg)
admin.site.register(Department)
admin.site.register(DoctorReg)
admin.site.register(PatientReg)
admin.site.register(Appointment)
admin.site.register(Medical_record)
admin.site.register(Medicie_details)
admin.site.register(Test_details)