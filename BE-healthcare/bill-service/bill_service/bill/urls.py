from django.urls import path
from . import views  # import views trong app

urlpatterns = [
    path('b/get-active-payment-method', views.get_active_payment_methods, name='get_active_payment_methods'),
    path('b/create-bill', views.create_bill, name='create_bill'),
    
]
