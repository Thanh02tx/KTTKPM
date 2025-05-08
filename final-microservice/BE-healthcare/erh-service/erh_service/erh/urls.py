from django.urls import path
from . import views

urlpatterns = [
    path('e/create-vital-sign', views.create_vital_sign, name='create_vital_sign'), 
    path('e/get-vitalsign-by-medical', views.get_vital_sign_by_medical_record, name='get_vital_sign_by_medical_record'), 
    path('e/create-diagnosis-and-test-requests', views.create_diagnosis_and_test_requests, name='create_diagnosis_and_test_requests'),
    path('e/get-diagnosis-by-medical', views.get_diagnosis_by_medical_record, name='get_diagnosis_by_medical_record'),     
    path('e/doctor-update-diagnosis-and-status', views.doctor_update_diagnosis_and_status, name='doctor_update_diagnosis_and_status'),     
    
]