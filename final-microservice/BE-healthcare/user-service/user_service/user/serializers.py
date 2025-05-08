from rest_framework import serializers
from .models import User, Doctor, Patient, Nurse, Technician, Pharmacist, BaseProfile,Cashier

# Serializer cho User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'is_staff']

# Base Profile Serializer (Tạo một serializer chung cho các profile)
class BaseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseProfile
        fields = ['id', 'user', 'image', 'name', 'gender', 'phone', 'date_of_birth', 'province', 'district', 'ward', 'address_detail']

# Doctor Serializer
class DoctorSerializer(BaseProfileSerializer):
    degree = serializers.CharField(max_length=100)
    description_html = serializers.CharField()
    price = serializers.IntegerField()
    exam_count = serializers.IntegerField(required=False, default=0)
    bio_html = serializers.CharField()

    class Meta(BaseProfileSerializer.Meta):
        model = Doctor
        fields = BaseProfileSerializer.Meta.fields + [
            'degree', 'description_html', 'price', 'exam_count', 'bio_html'
        ]

# Patient Serializer
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'image', 'name', 'gender', 'phone',
            'date_of_birth', 'province', 'district', 'ward', 'address_detail',
            'national_id', 'health_insurance'
        ]

# Nurse Serializer
class NurseSerializer(BaseProfileSerializer):
    bio_html = serializers.CharField(required=False)

    class Meta(BaseProfileSerializer.Meta):
        model = Nurse
        fields = BaseProfileSerializer.Meta.fields + ['bio_html']

# Technician Serializer
class TechnicianSerializer(BaseProfileSerializer):
    bio_html = serializers.CharField(required=False)

    class Meta(BaseProfileSerializer.Meta):
        model = Technician
        fields = BaseProfileSerializer.Meta.fields + ['bio_html']

# Pharmacist Serializer
class PharmacistSerializer(BaseProfileSerializer):
    bio_html = serializers.CharField(required=False)

    class Meta(BaseProfileSerializer.Meta):
        model = Pharmacist
        fields = BaseProfileSerializer.Meta.fields + ['bio_html']

class CashierSerializer(BaseProfileSerializer):
    bio_html = serializers.CharField(required=False)

    class Meta(BaseProfileSerializer.Meta):
        model = Cashier
        fields = BaseProfileSerializer.Meta.fields + ['bio_html']