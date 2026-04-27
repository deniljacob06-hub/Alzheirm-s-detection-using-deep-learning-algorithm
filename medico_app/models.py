from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Login(AbstractUser):
    user_type=models.CharField(max_length=30)
    view_password=models.CharField(max_length=30)

class HospitalReg(models.Model):
    hospital_log=models.ForeignKey(Login,on_delete=models.CASCADE)
    hospital_name=models.CharField(max_length=30)
    phone=models.CharField(max_length=30)
    email=models.EmailField()
    hospital_address=models.TextField()
    pincode=models.CharField(max_length=30)
    district=models.CharField(max_length=30)
    image=models.ImageField(null=True)
    licence=models.FileField(null=True)

class Department(models.Model):
    department_name=models.CharField(max_length=30)

class DoctorReg(models.Model):
    doctor_log=models.ForeignKey(Login,on_delete=models.CASCADE)
    hospital=models.ForeignKey(HospitalReg,on_delete=models.CASCADE,null=True)
    department=models.ForeignKey(Department,on_delete=models.CASCADE)
    fname=models.CharField(max_length=30)
    lname=models.CharField(max_length=30,null=True)
    phone=models.CharField(max_length=30)
    fee=models.CharField(max_length=30,default='200')
    email=models.EmailField()
    doctor_address=models.TextField()
    image=models.ImageField(null=True)
    time_from=models.TimeField(null=True)
    time_to=models.TimeField(null=True)
    highest_quali=models.CharField(max_length=30,null=True)
    quali_certi=models.FileField(null=True)

class PatientReg(models.Model):
    patient_log=models.ForeignKey(Login,on_delete=models.CASCADE)
    fname=models.CharField(max_length=30)
    lname=models.CharField(max_length=30,null=True)
    phone=models.CharField(max_length=30)
    email=models.EmailField()
    patient_address=models.TextField()
    gender=models.CharField(max_length=30)
    age=models.CharField(max_length=30,null=True)
    weight=models.CharField(max_length=30)

class py(models.Model):
    user=models.ForeignKey(PatientReg,on_delete=models.CASCADE)
    requests=models.CharField(max_length=100)
    status=models.ImageField(upload_to="profile",null=True)
    date=models.DateField(auto_now_add=True)
    gender=models.CharField(max_length=100)
    def __str__(self):
        return self.requests
class Requestuser(models.Model):
    user=models.ForeignKey(PatientReg,on_delete=models.CASCADE)
    status=models.ImageField(upload_to="profile",null=True)
    date=models.DateField(auto_now_add=True)
class Appointment(models.Model):
    patient=models.ForeignKey(PatientReg,on_delete=models.CASCADE)
    doctor=models.ForeignKey(DoctorReg,on_delete=models.CASCADE,null=True)
    app_date=models.DateField()
    booked_on=models.DateField(auto_now_add=True,null=True)
    app_time=models.CharField(max_length=30)
    app_status=models.CharField(max_length=30,default='Pending')
    paid_on=models.DateField(null=True)
    paytype=models.CharField(max_length=30,null=True)

class Medical_record(models.Model):
    appointment=models.ForeignKey(Appointment,on_delete=models.CASCADE,null=True)
    date_of_issue=models.DateField(auto_now_add=True)
    remarks=models.TextField()
    symptoms=models.TextField(null=True)
    next_app=models.DateField(null=True)

class Medicie_details(models.Model): 
    medical_record=models.ForeignKey(Medical_record,on_delete=models.CASCADE)   
    m_name=models.CharField(max_length=30)
    m_dosage=models.CharField(max_length=30)
    m_quantity=models.CharField(max_length=30)
    m_directions=models.CharField(max_length=30)
    m_days=models.CharField(max_length=30)

class Test_details(models.Model):
    medical_record=models.ForeignKey(Medical_record,on_delete=models.CASCADE)
    test_name=models.CharField(max_length=30)
    test_upload=models.FileField(blank=True)


    