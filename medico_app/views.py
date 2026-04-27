from django.shortcuts import render,redirect
from .models import *
from datetime import date,datetime,timedelta
from django.contrib.auth import authenticate
from django.contrib import messages
# Create your views here.
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
# def mse(imageA, imageB):
#     err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
#     err /= float(imageA.shape[0] * imageA.shape[1])
#     return err
# def compare_images(imageA, imageB, title):
#     out=0
#     m = mse(imageA, imageB)
#     s = ssim(imageA, imageB)
    
#     if(s>=.5 and s<=1):
#         out=1
#         msg="detected"
#     else:
#         msg="notdetected"
#     fig = plt.figure(title)
#     plt.suptitle("Similarity %s,Value %.2f"%(msg,s))
# 	# show first image
#     # 
#     ax = fig.add_subplot(1, 2, 1)
#     plt.imshow(imageA, cmap = plt.cm.gray)
#     plt.axis("off")
# 	# show the second image
#     ax = fig.add_subplot(1, 2, 2)
#     plt.imshow(imageB, cmap = plt.cm.gray)
#     plt.axis("off")
# 	# show the images
#     plt.show()
#     return out

import subprocess

def index(request):
    return render(request,'index.html')
def bot(request):
    subprocess.run(
    ["python", "chatgui.py"])
    return redirect("/patient-dashboard/")
def users_login(request):
    if request.POST:
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(username=email,password=password)
        if user is not None:
            if user.user_type=='admin':
                msg=messages.success(request,'Welcome to admin dashboard')
                return redirect('/admin-dashboard')
            elif user.user_type=='hospital':
                msg=messages.success(request,'Welcome to hospital dashboard')
                userregid=user
                hospitalid=HospitalReg.objects.get(hospital_log=userregid).id
                request.session['hid']=hospitalid
                return redirect('/hospital-dashboard')
            elif user.user_type=='patient':
                msg=messages.success(request,'Welcome to patient dashboard')
                patientregid=user
                patientid=PatientReg.objects.get(patient_log=patientregid).id
                request.session['pid']=patientid
                print(request.session['pid'])
                return redirect('/patient-dashboard')
            elif user.user_type=='doctor':
                msg=messages.success(request,'Welcome to doctor dashboard')
                doctorregid=user
                doctorid=DoctorReg.objects.get(doctor_log=doctorregid).id
                request.session['did']=doctorid
                return redirect('/doctor-dashboard')
        else:
            msg=messages.success(request,'Invalid Login again')
            return redirect('/users-login')
    return render(request,'users_login.html')

#admin
def admin_dashboard(request):
    return render(request,'admin/admin_dashboard.html')

def admin_approvehospital(request):
    hospitals=HospitalReg.objects.filter(hospital_log__is_active=0)
    return render(request,'admin/admin_approvehospital.html',{"hospitals":hospitals})

def admin_approvesinglehospital(request):
    hid=request.GET.get('hid')
    hospital=HospitalReg.objects.get(id=hid).hospital_log.id
    hlogin=Login.objects.filter(id=hospital).update(is_active=1)
    # print(hubid)
    msg=messages.success(request,'Hospital approved sucessfully')
    return redirect('/admin-viewhospitals')

def admin_viewhospitals(request):
    hospitals=HospitalReg.objects.filter(hospital_log__is_active=1)
    return render(request,'admin/admin_viewhospitals.html',{"hospitals":hospitals})

def admin_rejectsinglehospital(request):
    # print('reject')
    hid=request.GET.get('hid')
    # print(hubid)
    hospital=HospitalReg.objects.get(id=hid).hospital_log.id
    hlogin=Login.objects.filter(id=hospital).update(is_active=0)
    msg=messages.success(request,'Hospital rejected sucessfully')
    return redirect('/admin-viewhospitals')

def admin_viewdoctors(request):
    hospital=request.GET.get('hospitalid')
    print(hospital)
    departments=Department.objects.all().order_by('department_name')
    doctors=DoctorReg.objects.filter(hospital_id=hospital)
    print(doctors)
    if request.POST:
        department=request.POST['department']
        doctors=DoctorReg.objects.filter(hospital_id=hospital,department_id=department)
    return render(request,'admin/admin_viewdoctors.html',{"doctors":doctors,"departments":departments,"hospital":hospital})

def admin_adddepartments(request):
    if request.POST:
        department=request.POST['department']
        if Department.objects.filter(department_name__iexact=department).exists():
            msg=messages.success(request,'Department already added')
            return redirect('/admin-adddepartments')
        else:
            department=Department.objects.create(department_name=department)
            department.save()
            msg=messages.success(request,'Department name added sucessfully')
            return redirect('/admin-adddepartments')
    departments=Department.objects.all().order_by('department_name')
    return render(request,'admin/admin_adddepartments.html',{"departments":departments})

def admin_updatedepartment(request):
    did=request.GET.get('did')
    # print(brandid)
    department=Department.objects.get(id=did)
    if request.POST:
        department=request.POST['department']
        department=Department.objects.filter(id=did).update(department_name=department)
        msg=messages.success(request,'Department name updated sucessfully')
        return redirect('/admin-adddepartments')
    return render(request,'admin/admin_updatedepartment.html',{"department":department})

def admin_deletedepartment(request):
    did=request.GET.get('did')
    # print(brandid)
    department=Department.objects.filter(id=did).delete()
    msg=messages.success(request,'Department name deleted sucessfully')
    return redirect('/admin-adddepartments')

def admin_viewappointments(request):
    appointments=Appointment.objects.all().order_by("-id")
    return render(request,'admin/admin_viewappointments.html',{'appointments':appointments})

def admin_viewmedicalrecord(request):
    appointmentid=request.GET.get('appointmentid')
    patient=Appointment.objects.get(id=appointmentid).patient.id
    pdata=PatientReg.objects.get(id=patient)
    prescriptiondatas=Medical_record.objects.filter(appointment__patient_id=patient).order_by('-id')
    print(prescriptiondatas)
    medicines=Medicie_details.objects.all()
    print(medicines)
    tests=Test_details.objects.all()
    print(tests)
    return render(request,'admin/admin_viewmedicalrecord.html',{"prescriptions":prescriptiondatas,"medicines":medicines,"tests":tests,"pdata":pdata})

#hospital
def hospital_signup(request):
    if request.POST:
        name=request.POST['name']
        phone=request.POST['phone']
        image=request.FILES['image']
        email=request.POST['email']
        password=request.POST['password']
        district=request.POST['district']
        address=request.POST['address']
        pin=request.POST['pincode']
        licence=request.FILES['licence']
        if Login.objects.filter(username=email).exists():
            print('exists,,,,,,')
            msg=messages.success(request,'Already Taken')
            return redirect('/')
        else:
            h_login=Login.objects.create_user(user_type='hospital',view_password=password,username=email,password=password,is_active=0)
            h_login.save()
            hadd=HospitalReg.objects.create(hospital_log=h_login,hospital_name=name,image=image,phone=phone,
                                                email=email,district=district,hospital_address=address,pincode=pin,
                                                licence=licence)
            hadd.save()
            msg=messages.success(request,'Hospital added sucessfully, Wait for approval')
            return redirect('/')
    return render(request,'hospital_signup.html')

def hospital_dashboard(request):
    return render(request,'hospital/hospital_dashboard.html')

def hospital_adddoctor(request):
    departments=Department.objects.all().order_by('department_name')
    hospital=request.session['hid']
    print(hospital)
    if request.POST:
        fname=request.POST['fname']
        lname=request.POST['lname']
        phone=request.POST['phone']
        fee=request.POST['fee']
        image=request.FILES['image']
        email=request.POST['email']
        password=request.POST['password']
        hqualification=request.POST['hqualification']
        qcertificate=request.FILES['qcertificate']
        address=request.POST['address']
        department=request.POST['department']
        tfrom=request.POST['tfrom']
        tto=request.POST['tto']
        if Login.objects.filter(username=email).exists():
            print('exists,,,,,,')
            msg=messages.success(request,'Already Taken')
            return redirect('/hospital-adddoctor')
        else:
            d_login=Login.objects.create_user(user_type='doctor',view_password=password,username=email,password=password)
            d_login.save()
            dadd=DoctorReg.objects.create(doctor_log=d_login,hospital_id=hospital,department_id=department,fname=fname,fee=fee,lname=lname,image=image,phone=phone,
                                                email=email,highest_quali=hqualification,quali_certi=qcertificate,doctor_address=address,time_from=tfrom,
                                                time_to=tto)
            dadd.save()
            msg=messages.success(request,'Doctor added sucessfully')
            return redirect('/hospital-viewdoctors')
    return render(request,'hospital/hospital_adddoctor.html',{"departments":departments})

def hospital_viewdoctors(request):
    hospital=request.session['hid']
    print(hospital)
    departments=Department.objects.all().order_by('department_name')
    doctors=DoctorReg.objects.filter(hospital_id=hospital)
    print(doctors)
    if request.POST:
        department=request.POST['department']
        doctors=DoctorReg.objects.filter(hospital_id=hospital,department_id=department)
    return render(request,'hospital/hospital_viewdoctors.html',{"doctors":doctors,"departments":departments})

def hospital_viewdocappointments(request):
    doctor=request.GET.get('docid')
    print(doctor)
    appointments=Appointment.objects.filter(doctor_id=doctor).order_by("-id")
    print(appointments,'appointmentsffffffffff')
    return render(request,'hospital/hospital_viewdocappointments.html',{'appointments':appointments})

def hospital_viewmedicalrecord(request):
    appointmentid=request.GET.get('appointmentid')
    patient=Appointment.objects.get(id=appointmentid).patient.id
    pdata=PatientReg.objects.get(id=patient)
    prescriptiondatas=Medical_record.objects.filter(appointment__patient_id=patient).order_by('-id')
    print(prescriptiondatas)
    medicines=Medicie_details.objects.all()
    print(medicines)
    tests=Test_details.objects.all()
    print(tests)
    return render(request,'hospital/hospital_viewmedicalrecord.html',{"prescriptions":prescriptiondatas,"medicines":medicines,"tests":tests,"pdata":pdata})

def hospital_viewprofile(request):
    hospital=request.session['hid']
    print(hospital)
    hdata=HospitalReg.objects.get(id=hospital)
    return render(request,'hospital/hospital_viewprofile.html',{"data":hdata})

def hospital_updateprofile(request):
    hospitalid=request.GET.get('hid')
    hospital=HospitalReg.objects.get(id=hospitalid)
    if request.POST:
        phone=request.POST['phone']
        if 'image' in request.FILES:
            image=request.FILES['image']
        else:
            image=hospital.image
        if 'district' in request.POST:
            district=request.POST['district']
        else:
            district=hospital.district
        address=request.POST['address']
        pin=request.POST['pincode']
        hup=HospitalReg.objects.filter(id=hospitalid).update(image=image,phone=phone,district=district,hospital_address=address,pincode=pin)
        msg=messages.success(request,'Hospital updated sucessfully')
        return redirect('/hospital-viewprofile')
    return render(request,'hospital/hospital_updateprofile.html',{"data":hospital})

#patient
def patient_signup(request):
    if request.POST:
        fname=request.POST['fname']
        lname=request.POST['lname']
        phone=request.POST['phone']
        email=request.POST['email']
        password=request.POST['password']
        address=request.POST['address']
        gender=request.POST['gender']
        age=request.POST['age']
        weight=request.POST['weight']
        if Login.objects.filter(username=email).exists():
            print('exists,,,,,,')
            msg=messages.success(request,'Already Taken')
            return redirect('/patient-signup')
        else:
            p_login=Login.objects.create_user(user_type='patient',view_password=password,username=email,password=password)
            p_login.save()
            padd=PatientReg.objects.create(patient_log=p_login,gender=gender,age=age,fname=fname,lname=lname,
                                           weight=weight,phone=phone,email=email,patient_address=address)
            padd.save()
            msg=messages.success(request,'Patient added sucessfully')
            return redirect('/users-login')
    return render(request,'patient_signup.html')

def patient_dashboard(request):
    return render(request,'patient/patient_dashboard.html')
import alzimers as al
def Uploadimage(request):
    data=""
    # try:
    if request.POST:
        pid=request.session["pid"]
        user=PatientReg.objects.get(id=pid)
        # requ=request.POST["t1"]
        type=request.FILES["img"]
        
        print("***********************",type,"****************")
        # gender=request.POST["t3"]
        al.alzhim(type)
        req=Requestuser.objects.create(user=user,status=type)
        req.save()
        ss=str("static/media/profile/")+str(type.name)
        data=al.alzhim(ss)
                # break
            
            # fig = plt.figure("Images")
            # images = ("Original", original), ("Contrast", contrast)
            # # loop over the images
            # for (i, (name, image)) in enumerate(images):
            #     # show the image
            #     ax = fig.add_subplot(1, 2, i + 1)
            #     ax.set_title(name)
            #     plt.imshow(image, cmap = plt.cm.gray)
            #     plt.axis("off")
            # # show the figure
            # plt.show()
            # compare the images
            #compare_images(original, original, "Original vs. Original")
    # except:
    #     msg="not detected"
    return render(request,"patient/detection.html",{"msg":data})
def Uploadimages(request):
    data=""
    # try:
    if request.POST:
        pid=request.session["pid"]
        user=CustomUser.objects.get(id=pid)
        # requ="test"
        type=request.FILES["img"]
        
        print("***********************",type,"****************")
        # gender=request.POST["t3"]
        al.alzhim(type)
        req=Requestuser.objects.create(user=user,status=type)
        req.save()
        ss=str("static/media/profile/")+str(type.name)
        data=al.alzhim(ss)
                # break
            
            # fig = plt.figure("Images")
            # images = ("Original", original), ("Contrast", contrast)
            # # loop over the images
            # for (i, (name, image)) in enumerate(images):
            #     # show the image
            #     ax = fig.add_subplot(1, 2, i + 1)
            #     ax.set_title(name)
            #     plt.imshow(image, cmap = plt.cm.gray)
            #     plt.axis("off")
            # # show the figure
            # plt.show()
            # compare the images
            #compare_images(original, original, "Original vs. Original")
    # except:
    #     msg="not detected"
    return render(request,"Uploadimage2.html",{"msg":data})

def patient_viewhospitals(request):
    hospitals=HospitalReg.objects.filter(hospital_log__is_active=1)
    return render(request,'patient/patient_viewhospitals.html',{"hospitals":hospitals})

def patient_viewdoctors(request):
    hospital=request.GET.get('hospitalid')
    print(hospital)
    departments=Department.objects.all().order_by('department_name')
    doctors=DoctorReg.objects.filter(hospital_id=hospital)
    print(doctors)
    if request.POST:
        department=request.POST['department']
        doctors=DoctorReg.objects.filter(hospital_id=hospital,department_id=department)
    return render(request,'patient/patient_viewdoctors.html',{"doctors":doctors,"departments":departments,"hospital":hospital})

def patient_makeappointment(request):
    period_list=[]
    doctorid=request.GET.get('docid')
    print(doctorid)
    bdate = request.GET.get('bdate')
    print(bdate,'bdatellllllll')
    formatted_date = None

    if bdate:
        bdate = bdate.replace(".", '').replace('Sept', 'Sep').replace('March', 'Mar').replace('April', 'Apr').replace('June', 'Jun').replace('July', 'Jul')
        print(bdate)
        try:
            date_obj = datetime.strptime(bdate, '%b %d, %Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            print(formatted_date, 'formatted_datellllll')
        except ValueError:
            print("Invalid date format:", bdate)
    doctor=DoctorReg.objects.get(id=doctorid)
    patient=request.session['pid']
    print(patient)
    patient=PatientReg.objects.get(id=patient)
    def split_time_range(start_time, end_time, interval_minutes):
        current_time = start_time
        time_periods = []
        while current_time < end_time:
            time_periods.append(current_time)
            current_time = (datetime.combine(datetime.min, current_time) + timedelta(minutes=interval_minutes)).time()
        return time_periods
    start_time = doctor.time_from
    end_time = doctor.time_to
    interval_minutes = 30
    time_periods = split_time_range(start_time, end_time, interval_minutes)
    for period in time_periods:
        print(period.strftime("%I:%M %p"), 'bbbbbbbbbbbbb')
        period_list.append(period.strftime("%I:%M %p"))
    if request.POST:
        app_date=request.POST['app_date']
        app_time=request.POST['inlineRadioOptions']
        print(app_date,app_time,'app_')
        if Appointment.objects.filter(doctor=doctor,app_date=app_date,app_time=app_time):
            msg=messages.success(request,'Appointment time already taken')
            return redirect('/patient-viewappointments')
        else:
            app_add=Appointment.objects.create(patient=patient,doctor=doctor,app_date=app_date,app_time=app_time)
            app_add.save()
            msg=messages.success(request,'Your appoint request has been send, wait for doctors action')
            return redirect('/patient-viewappointments')
    return render(request,'patient/patient_makeappointment.html',{"doctor":doctor,"patient":patient,"periods":period_list,"formatted_date":formatted_date})

def patient_viewappointments(request):
    patient=request.session['pid']
    print(patient)
    print('hiiiiiiiiiii')
    appointments=Appointment.objects.filter(patient_id=patient)
    print(appointments)
    return render(request,'patient/patient_viewappointments.html',{"appointments":appointments})

def patient_cancelappointment(request):
    appointmentid=request.GET.get('appointmentid')
    print(appointmentid)
    appointment=Appointment.objects.filter(id=appointmentid).update(app_status='Cancel')
    msg=messages.success(request,'You cancelled the appointment')
    return redirect('/patient-viewappointments')

def patient_payfeeappointment(request):
    appointmentid=request.GET.get('appointmentid')
    print(appointmentid)
    appointment=Appointment.objects.get(id=appointmentid)
    if request.POST:
        return redirect('/patient-addcarddetails?appointmentid='+str(appointmentid))
    return render(request,'patient/patient_payfeeappointment.html',{"appointment":appointment})

def patient_addcarddetails(request):
    appointmentid=int(request.GET.get('appointmentid'))
    if request.POST:
        pdate=date.today()
        ptype='Debit Card'
        appointment=Appointment.objects.filter(id=appointmentid).update(paid_on=pdate,paytype=ptype,app_status="Confirm")
        msg=messages.success(request,'Payment sucess, Appointment confirmed')
        return redirect('/patient-viewappointments')
    return render(request,'patient/patient_addcarddetails.html')

def patient_viewprescription(request):
    appointmentid=request.GET.get('appointmentid')
    print(appointmentid)
    appointmentdata=Appointment.objects.get(id=appointmentid)
    prescriptiondata=Medical_record.objects.get(appointment=appointmentid)
    medicines=Medicie_details.objects.filter(medical_record=prescriptiondata)
    tests=Test_details.objects.filter(medical_record=prescriptiondata)
    return render(request,'patient/patient_viewprescription.html',{"appointment":appointmentdata,"prescription":prescriptiondata,"medicines":medicines,"tests":tests})

def patient_viewmedicalrecord(request):
    patient=request.session['pid']
    print(patient)
    pdata=PatientReg.objects.get(id=patient)
    if request.POST:
        tres=request.FILES['tupload']
        testid=request.POST['tid']
        print(tres,testid)
        tresult=Test_details.objects.filter(id=testid).update(test_upload=tres)
        msg=messages.success(request,'Test Result uploaded sucessfully')
    prescriptiondatas=Medical_record.objects.filter(appointment__patient_id=patient).order_by('-id')
    print(prescriptiondatas)
    medicines=Medicie_details.objects.all()
    print(medicines)
    tests=Test_details.objects.all()
    print(tests)
    return render(request,'patient/patient_viewmedicalrecord.html',{"prescriptions":prescriptiondatas,"medicines":medicines,"tests":tests,"pdata":pdata})

# def patient_viewprofile(request):
#     return render(request,'patient/patient_viewprofile.html')

#doctor
def doctor_dashboard(request):
    return render(request,'doctor/doctor_dashboard.html')

def doctor_viewappointments(request):
    msg=""
    doctor=request.session['did']
    print(doctor)
    doctor=DoctorReg.objects.get(id=doctor)
    today = date.today()
    print(today,'datemmmmz')
    appointments=Appointment.objects.filter(doctor=doctor,app_date=today)
    ddate=today
    
    if request.POST:
        ddate=request.POST['ddate']
        if ddate:
            appointments=Appointment.objects.filter(doctor=doctor,app_date=ddate)
        else:
            msg="No appointment"
    return render(request,'doctor/doctor_viewappointments.html',{'appointments':appointments,'app_date':ddate,"message":msg,'today':today})

def doctor_approveappointment(request):
    appointmentid=request.GET.get('appointmentid')
    print(appointmentid)
    appointment=Appointment.objects.filter(id=appointmentid).update(app_status='Approve')
    msg=messages.success(request,'You approved the appointment wait for users payment')
    return redirect('/doctor-viewappointments')

def doctor_rejectappointment(request):
    appointmentid=request.GET.get('appointmentid')
    print(appointmentid)
    appointment=Appointment.objects.filter(id=appointmentid).update(app_status='Reject')
    msg=messages.success(request,'You rejected the appointment')
    return redirect('/doctor-viewappointments')

def doctor_markstatus(request):
    appointmentid=request.GET.get('appointmentid')
    print(appointmentid)
    status=request.GET.get('status')
    print(status)
    if status=='Visited':
        appointment=Appointment.objects.filter(id=appointmentid).update(app_status='Visited')
        msg=messages.success(request,'Patient visited')
        return redirect('/doctor-viewappointments')
    elif status=='Not Visited':
        appointment=Appointment.objects.filter(id=appointmentid).update(app_status='Not Visited')
        msg=messages.success(request,'Patient not visited')
        return redirect('/doctor-viewappointments')
    return redirect('/doctor-viewappointments')

def doctor_addmedical(request):
    appointmentid=request.GET.get('appointmentid')
    appointment=Appointment.objects.get(id=appointmentid)

    if request.method == 'POST':
        symptoms = request.POST.get('symptoms')
        remarks = request.POST.get('remarks')
        print(remarks,'remarksd')
        medicine_names = request.POST.getlist('medicine_name')
        medicine_dosages = request.POST.getlist('medicine_dosage')
        medicine_quantitys = request.POST.getlist('medicine_quantity')
        medicine_directionss = request.POST.getlist('medicine_directions')
        medicine_dayss = request.POST.getlist('medicine_days')
        test_names = request.POST.getlist('test_name')
        bdate = request.POST.get('bdate')
        medicines = [{'name': name, 'dosage': dosage, 'quantity': quantity, 'directions': directions, 'days': 
                      days} for name, dosage, quantity, directions, days in zip(medicine_names, medicine_dosages,
                     medicine_quantitys, medicine_directionss, medicine_dayss)]
        tests=[{'name':name} for name in (test_names)]
        print(remarks,medicines,tests,bdate)
        
        #adding new row to Medical_record with booking date
        if bdate:
            prescription_data=Medical_record.objects.create(appointment=appointment,symptoms=symptoms,
                                                            remarks=remarks,next_app=bdate)
            prescription_data.save()
        else:
            prescription_data=Medical_record.objects.create(appointment=appointment,symptoms=symptoms,
                                                            remarks=remarks)
            prescription_data.save()

        #adding new row to Medicine_details
        medicineslist_length=(len(medicines))
        for item in range(medicineslist_length):
            medicine_data=Medicie_details.objects.create(medical_record=prescription_data,m_name=
            medicines[item]['name'],m_dosage=medicines[item]['dosage'],m_quantity=medicines[item]['quantity'],
            m_directions=medicines[item]['directions'],m_days=medicines[item]['days'])
            medicine_data.save()
        
        #adding new row to Test_details
        testslist_length=(len(tests))
        for item in range(testslist_length):
            test_data = Test_details.objects.create(medical_record=prescription_data, test_name=tests[item]['name'])
            test_data.save()
        appointment=Appointment.objects.filter(id=appointmentid).update(app_status='Prescription added')
        msg=messages.success(request,'Prescription added')
        return redirect('/doctor-viewappointments')
    
    return render(request,'doctor/doctor_addmedical.html')

def doctor_viewmedicalrecord(request):
    appointmentid=request.GET.get('appointmentid')
    patient=Appointment.objects.get(id=appointmentid).patient.id
    pdata=PatientReg.objects.get(id=patient)
    prescriptiondatas=Medical_record.objects.filter(appointment__patient_id=patient).order_by('-id')
    print(prescriptiondatas)
    medicines=Medicie_details.objects.all()
    print(medicines)
    tests=Test_details.objects.all()
    print(tests)
    return render(request,'doctor/doctor_viewmedicalrecord.html',{"prescriptions":prescriptiondatas,"medicines":medicines,"tests":tests,"pdata":pdata})
# patient=request.session['pid']
#     print(patient)
#     pdata=PatientReg.objects.get(id=patient)
    # if request.POST:
    #     tres=request.FILES['tupload']
    #     testid=request.POST['tid']
    #     print(tres,testid)
    #     tresult=Test_details.objects.filter(id=testid).update(test_upload=tres)
    #     msg=messages.success(request,'Test Result uploaded sucessfully')
    # prescriptiondatas=Medical_record.objects.filter(appointment__patient_id=patient).order_by('-id')
    # print(prescriptiondatas)
    # medicines=Medicie_details.objects.all()
    # print(medicines)
    # tests=Test_details.objects.all()
    # print(tests)
    # return render(request,'patient/patient_viewmedicalrecord.html',{"prescriptions":prescriptiondatas,"medicines":medicines,"tests":tests,"pdata":pdata})