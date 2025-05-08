from django.urls import path
from . import views

urlpatterns = [
    path('a/create-room', views.create_room, name='create_room'), 
    path('a/get-rooms', views.get_rooms, name='get_rooms'), 
    path('a/change-active-room', views.change_active_room, name='change_active_room'),
    path('a/get-room-by-id', views.get_room_by_id, name='get_room_by_id'),
    path('a/update-room', views.update_room, name='update_room'),
    path('a/get-times', views.get_times, name='get_times'), 
    path('a/create-schedules-and-timeslots', views.create_schedules_and_timeslot, name='create_schedules_and_timeslot'), 
    
    path('a/get-schedules', views.get_schedules, name='get_schedules'),
    path('a/get-medical-by-id', views.get_medical_record_by_id, name='get_medical_record_by_id'),
    path('a/get-schedules-week', views.get_schedules_week, name='get_schedules_week'), 
    path('a/get-timeslots', views.get_timeslots, name='get_timeslots'), 
    path('a/get-timeslots-by-date-doctorid', views.get_timeslots_by_date_and_doctorid, name='get_timeslots_by_date_and_doctorid'), 
    path('a/get-schedule-doctor-by-timeslotid', views.get_schedule_doctor_by_timeslotid, name='get_schedule_doctor_by_timeslotid'), 
    path('a/check-duplicate-appointment', views.check_duplicate_appointment, name='check_duplicate_appointment'),
    path('a/create-appointment-with-medical-record', views.create_appointment_with_medical_record, name='create_appointment_with_medical_record'),
    
    path('a/get-medicals', views.get_medicals, name='get_medicals'), 
    path('a/get-appointments', views.get_appointments, name='get_appointments'), 
    path('a/get-appointment-medical-by-nurse-and-date', views.get_appointment_medical_by_nurse_date, name='get_appointment_medical_by_nurse_date'), 
    path('a/get-appointment-medical-by-doctor-and-date', views.get_appointment_medical_by_doctor_date, name='get_appointment_medical_by_doctor_date'), 
    path('a/get-appointment-medical-by-pharmacist-and-date', views.get_appointment_medical_by_pharmacist_date, name='get_appointment_medical_by_pharmacist_date'), 
    
    path('a/get-cashier-appointment-medical-by-date', views.get_cashier_appointment_medical_by_date, name='get_cashier_appointment_medical_by_date'), 
    path('a/change-status-appointment', views.change_status_appointment, name='change_status_appointment'), 
    path('a/change-payment-status-appointment', views.change_payment_status_appointment, name='change_payment_status_appointment'), 
    
    path('a/mark-appointment-paid', views.mark_appointment_paid, name='mark_appointment_paid'), 
    path('a/get-appointment-medical-testrequest-paid-by-date', views.get_appointment_medical_testrequest_paid_by_date, name='get_appointment_medical_testrequest_paid_by_date'), 
    path('a/get-history-appointment-by-patient', views.get_history_appointments_by_patient, name='get_history_appointments_by_patient'), 

]