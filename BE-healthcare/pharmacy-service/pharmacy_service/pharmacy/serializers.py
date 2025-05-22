from rest_framework import serializers
from .models import Medicine, Prescription, PrescriptionMedicine, Invoice,PaymentMethod

# Serializer cho model Medicine
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'  # Lấy tất cả các trường trong model

# Serializer cho model Prescription
class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'  # Lấy tất cả các trường trong model

# Serializer cho model PrescriptionMedicine
class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = '__all__'  # Lấy tất cả các trường trong model

# Serializer cho model Invoice
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'  # Lấy tất cả các trường trong model
class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__' 