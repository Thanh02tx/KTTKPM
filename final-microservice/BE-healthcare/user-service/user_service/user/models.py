from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# ----------- CUSTOM USER MANAGER -----------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email, password, role='admin', is_superuser=True, is_staff=True, **extra_fields)


# ----------- CUSTOM USER MODEL -----------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('patient', 'Patient'),
        ('pharmacist', 'Pharmacist'),
        ('technician', 'Technician'),
        ('cashier', 'Cashier'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    class Meta:
        db_table = 'users'




# ----------- COMMON BASE PROFILE -----------
class BaseProfile(models.Model):
    GENDER_CHOICES = [('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.TextField() 
    name = models.CharField(max_length=500)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100, null=True, blank=True)
    address_detail = models.CharField(max_length=255)

    class Meta:
        abstract = True

# ----------- DOCTOR MODEL -----------
class Doctor(BaseProfile):
    degree = models.CharField(max_length=100)
    description_html=models.TextField()
    price = models.IntegerField()
    exam_count = models.PositiveIntegerField(default=0)
    bio_html = models.TextField()

    def __str__(self):
        return f"Dr. {self.name}"
    class Meta:
        db_table = 'doctors'



# ----------- NURSE MODEL -----------
class Nurse(BaseProfile):
    bio_html = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Nurse: {self.name}"
    class Meta:
        db_table = 'nurses'
        
class Technician(BaseProfile):
    bio_html = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Technician: {self.name}"
    class Meta:
        db_table = 'technicians'
# ----------- PHARMACIST MODEL -----------
class Pharmacist(BaseProfile):
    bio_html = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pharmacist: {self.name}"
    class Meta:
        db_table = 'pharmacists'
        
class Cashier(BaseProfile):
    bio_html = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cashier: {self.name}"

    class Meta:
        db_table = 'cashiers'
        
        
# ----------- PATIENT MODEL -----------
class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients')
    
    image = models.TextField() 
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

    class Meta:
        db_table = 'patients'
    def __str__(self):
        return f"Patient: {self.name}"
