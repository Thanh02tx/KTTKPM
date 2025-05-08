# user/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('u/doctors', views.get_all_doctors, name='get_all_doctors'),  # Định nghĩa URL cho việc lấy danh sách bác sĩ
    path('u/get-gender-choices', views.get_gender_choices, name='get_gender_choices'), 
    path('u/register-patient', views.register_patient, name='register_patient'), 
    path('u/login', views.login, name='registeloginr_patient'), 
    path('u/get-email-from-token', views.get_email_from_token, name='get_email_from_token'), 
    
    path('u/check-role-admin', views.check_admin_role, name='check_admin_role'), 
    path('u/check-role-nurse', views.check_nurse_role, name='check_nurse_role'), 
    path('u/check-role-doctor', views.check_doctor_role, name='check_doctor_role'), 
    path('u/check-role-cashier', views.check_cashier_role, name='check_cashier_role'), 
    path('u/check-role-technician', views.check_technician_role, name='check_technician_role'), 
    path('u/check-role-pharmacist', views.check_pharmacist_role, name='check_pharmacist_role'),     
    
    path('u/create-doctor',views.create_doctor,name='create_doctor'),
    path('u/get-all-doctor-admin',views.get_all_doctor_with_user_status,name='get_all_doctor_with_user_status'),
    path('u/change-active-user',views.change_active_user,name='change_active_user'),
    path('u/get-doctor',views.get_doctor,name='get_doctor'),
    path('u/get-doctor-by-token',views.get_doctor_by_token,name='get_doctor_by_token'),
    
    path('u/update-doctor',views.update_doctor,name='update_doctor'),
    
    path('u/create-nurse',views.create_nurse,name='create_nurse'),
    path('u/get-all-nurse-admin',views.get_all_nurse_with_user_status,name='get_all_nurse_with_user_status'),
    path('u/get-nurse',views.get_nurse,name='get_nurse'),
    path('u/update-nurse',views.update_nurse,name='update_nurse'),
    
    path('u/create-technician',views.create_technician,name='create_technician'),
    path('u/get-technician-by-token',views.get_technician_by_token,name='get_technician_by_token'),    
    path('u/get-pharmacist-by-token',views.get_pharmacist_by_token,name='get_pharmacist_by_token'),    
    path('u/get-all-technician-admin',views.get_all_technician_with_user_status,name='get_all_technician_with_user_status'),
    path('u/get-technician',views.get_technician,name='get_technician'),
    path('u/update-technician',views.update_technician,name='update_technician'),
    
    path('u/create-pharmacist',views.create_pharmacist,name='create_pharmacist'),
    path('u/get-all-pharmacist-admin',views.get_all_pharmacist_with_user_status,name='get_all_pharmacist_with_user_status'),
    path('u/get-pharmacist',views.get_pharmacist,name='get_pharmacist'),
    path('u/update-pharmacist',views.update_pharmacist,name='update_pharmacist'),
    
    path('u/create-cashier',views.create_cashier,name='create_cashier'),
    path('u/get-all-cashier-admin',views.get_all_cashier_with_user_status,name='get_all_cashier_with_user_status'),
    path('u/get-cashier',views.get_cashier,name='get_cashier'),
    path('u/get-cashier-by-token',views.get_cashier_by_token,name='get_cashier_by_token'),
    
    path('u/update-cashier',views.update_cashier,name='update_cashier'),
    
    path('u/get-select-all-nurse',views.get_select_all_nurse,name='get_select_all_nurse'),
    path('u/get-select-all-doctor',views.get_select_all_doctor,name='get_select_all_doctor'),
    path('u/get-all-doctor-home',views.get_all_doctor_home,name='get_all_doctor_home'),
    path('u/get-doctor-by-user-id',views.get_doctor_by_user_id,name='get_doctor_by_user_id'),
    
    path('u/create-patient-record',views.create_patient_record,name='create_patient_record'),
    path('u/get-all-patient-records-by-user',views.get_all_patient_records_by_user,name='get_all_patient_records_by_user'),
    path('u/get-patient-record-by-id', views.get_patient_record_by_id, name='get_patient_record_by_id'),
    path('u/update-patient-record', views.update_patient_record, name='update_patient_record'),
    
    
    
]
