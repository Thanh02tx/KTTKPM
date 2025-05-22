from rest_framework import serializers
from .models import TypeTest, TestRequest, TestResult

class TypeTestSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = TypeTest
        fields = '__all__'


class TestRequestSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = TestRequest
        fields = '__all__'


class TestResultSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = TestResult
        fields = '__all__'
