from djongo import models
from bson import ObjectId


# Create your models here.
class TypeTest(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    name = models.CharField(max_length=100)
    price = models.CharField(max_length=50)
    estimated_time = models.IntegerField(help_text="Estimated result time in minutes") #thoi gian thuc hien
    sample_type = models.CharField(max_length=100,blank=True, null=True)  # Mẫu bệnh phầm
    preparation = models.TextField(blank=True, null=True) #Hướng dẫn cb
    is_active = models.BooleanField(default=True)
    type = models.CharField(
        max_length=20,
        choices=[
            ("lab_test", "Xét nghiệm"),   # Xét nghiệm (có mẫu)
            ("ultrasound", "Siêu âm")        # Siêu âm (trả kết quả ngay)
        ],
        default="lab_test"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

    class Meta:
        db_table = "typetests"

class TestRequest(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    medical_record_id = models.CharField(max_length=100)
    typetest_id = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("unpaid", "Unpaid"),
            ("paid", "Paid")
        ],
        default="unpaid"
    )
    
    process_status = models.CharField(
        max_length=30,
        choices=[
            ("not_started", "Not Started"),
            ("processing", "Processing"),
            ("completed", "Completed")
        ],
        default="not_started"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

    class Meta:
        db_table = "testrequests"  

class TestResult(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)
    test_request_id = models.CharField(max_length=100)  # Liên kết tới TestRequest  
    conclusion = models.TextField(blank=True, null=True)  # Kết luận (optional)
    raw_image = models.CharField(max_length=100,blank=True,null=True)
    annotated_image = models.CharField(max_length=100,blank=True,null=True)
    technician_id= models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "testresults"      
        

