from rest_framework import serializers
from .models import VitalSign, Diagnosis

class VitalSignSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = VitalSign
        fields = '__all__'


class DiagnosisSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    medical_history = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_history = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    drug_allergy = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    final_diagnosis = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = Diagnosis
        fields = '__all__'
