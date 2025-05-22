from django.urls import path
from . import views  # import views trong app

urlpatterns = [
    path('p/create-medicine', views.create_medicine, name='create_medicine'),
    path('p/get-all-medicines', views.get_all_medicines, name='get_all_medicines'),
    path('p/get-all-medicines-active-select', views.get_all_medicines_active, name='get_all_medicines_active'),
    path('p/create-prescription-and-prescription-medicines', views.create_prescription_and_prescription_medicines, name='get_acreate_prescription_and_prescription_medicinesll_medicines_active'),
    path('p/get-prescription-by-medical-id', views.get_prescription_by_medical_id, name='get_prescription_by_medical_id'),
    path('p/get-active-payment-method', views.get_active_payment_methods, name='get_active_payment_methods'),
    path('p/create-invoice', views.create_invoice, name='create_invoice'),
    path('p/get-image-prescription-by-medical-id', views.get_image_prescription_by_medical_id, name='get_image_prescription_by_medical_id'),
    
]
