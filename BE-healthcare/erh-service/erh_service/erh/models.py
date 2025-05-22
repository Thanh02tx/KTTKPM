from djongo import models
from bson import ObjectId

class VitalSign(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    medical_id = models.CharField(max_length=50)
    blood_pressure = models.CharField(max_length=10, null=True)  # ví dụ "120/80"
    heart_rate = models.IntegerField(null=True) # nhịp tim
    height = models.FloatField(null=True)  # Chiều cao của bệnh nhân (mét)
    weight = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vital_signs"
    def __str__(self):
        return f"VitalSign  {self.id}"
    
class Diagnosis(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    vital_sign_id = models.CharField(max_length=50)
    medical_id = models.CharField(max_length=50)
    # Tiền sử bệnh nhân
    medical_history = models.TextField(null=True, blank=True)  # Tiền sử bệnh
    family_history = models.TextField(null=True, blank=True)  # Tiền sử gia đình
    drug_allergy = models.TextField(null=True, blank=True)  # Dị ứng thuốc

    # Chẩn đoán sơ bộ của bác sĩ
    preliminary_diagnosis = models.TextField()  # Chẩn đoán sơ bộ
    # Kết luận cuối cùng của bác sĩ
    final_diagnosis = models.TextField(null=True, blank=True)  # Chẩn đoán xác định
    image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian tạo
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "diagnosis"

    def __str__(self):
        return f"Diagnosis of Patient {self.id}"
    