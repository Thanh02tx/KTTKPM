
from django.contrib import admin
from django.urls import path, include  # thêm include vào để sử dụng với các ứng dụng khác

urlpatterns = [
    path('api/', include('bill.urls')),  # sử dụng include để chỉ định các url trong ứng dụng 'user'
]