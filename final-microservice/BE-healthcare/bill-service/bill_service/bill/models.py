# models.py - MySQL App
from django.db import models


class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # Ví dụ: "Tiền mặt", "Chuyển khoản", "Momo"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'payment_methods'


class Bill(models.Model):
    id = models.AutoField(primary_key=True)
    medical_id = models.CharField(max_length=50)
    cashier_id = models.CharField(max_length=50)
    total = models.IntegerField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    image = models.TextField(default="") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id}"

    class Meta:
        db_table = 'bills'
