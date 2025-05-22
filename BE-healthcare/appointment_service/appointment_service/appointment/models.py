from djongo import models
from bson import ObjectId


class Room(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "rooms"


class Schedule(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    doctor_id = models.CharField(max_length=50)
    nurse_id = models.CharField(max_length=50)
    date = models.DateField()
    room_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.date} - Doctor {self.doctor_id} - {self.id}"

    class Meta:
        db_table = "schedules"


class Time(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    time = models.CharField(max_length=20)

    def __str__(self):
        return self.time

    class Meta:
        db_table = "times"


class TimeSlot(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    schedule_id = models.CharField(max_length=50)
    time_id = models.CharField(max_length=50)
    current_number = models.IntegerField(default=0)
    max_number = models.IntegerField()

    def __str__(self):
        return f"Slot {self.time_id} ({self.current_number}/{self.max_number})"

    class Meta:
        db_table = "timeslots"

class MedicalRecord(models.Model): 
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    patient_id= models.CharField(max_length=50)
    name = models.CharField(max_length=500)
    gender = models.CharField(max_length=10, choices=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')])
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100, null=True, blank=True)
    address_detail = models.CharField(max_length=255)
    national_id = models.CharField(max_length=12)
    health_insurance = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}-{self.id} "

    class Meta:
        db_table = "medical_records"
    
class Appointment(models.Model):
    STATUS_CHOICES = [
    ('booked', 'Đã đặt'),
    ('ready_for_doctor', 'Đã nhập sinh tồn, chờ bác sĩ'),
    ('waiting_result', 'Chờ kết quả'),
    ('prescribed', 'Đã kê đơn thuốc'),
    ('done', 'Đã khám xong'),
    ('rated', 'Đã đánh giá'),
    ('cancelled', 'Đã huỷ'),
    ]

    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    medical_id = models.CharField(max_length=50)
    timeslot_id = models.CharField(max_length=50)
    reason = models.CharField(max_length=500)
    doctor_fee = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.patient_id} - {self.status}"

    class Meta:
        db_table = "appointments"
