from rest_framework import serializers
from .models import Room, Schedule, Time, TimeSlot, Appointment,MedicalRecord


class RoomSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Room
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'


class TimeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Time
        fields = '__all__'


class TimeSlotSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = TimeSlot
        fields = '__all__'

class MedicalRecordSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = MedicalRecord
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Appointment
        fields = '__all__'

