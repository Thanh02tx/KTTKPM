from django.db import models

# Thuốc
class Medicine(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    price = models.IntegerField(help_text="Giá của thuốc (đơn vị: VND)")
    stock = models.IntegerField(default=0, help_text="Số lượng thuốc còn trong kho (tồn kho)")
    description_html = models.TextField(blank=True, help_text="Mô tả HTML chi tiết thuốc")
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'medicines'


# Đơn thuốc
class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ bán thuốc'),
        ('sold', 'Đã bán xong'),
    ]

    id = models.AutoField(primary_key=True)
    medical_id = models.CharField(max_length=50, help_text="ID cuộc hẹn")
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Trạng thái đơn thuốc"
    )
    image = models.TextField(blank=True,null=True)
    note=models.TextField(blank=True,null=True)
    created_at = models.DateField(auto_now_add=True, help_text="Ngày tạo đơn thuốc")

    def __str__(self):
        return f"Đơn thuốc #{self.id} - {self.get_status_display()}"

    class Meta:
        db_table = 'prescriptions'



# Thuốc trong đơn thuốc
class PrescriptionMedicine(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chưa bán'),
        ('sold', 'Đã bán'),
    ]

    id = models.AutoField(primary_key=True)
    prescription = models.ForeignKey(Prescription, related_name='medicines', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    price = models.IntegerField(help_text="Giá thuốc tại thời điểm kê đơn")
    quantity = models.PositiveIntegerField(help_text="Số lượng thuốc trong đơn")
    directions_for_use=models.TextField(blank=True,null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Trạng thái bán thuốc"
    )

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} {self.medicine.unit})"

    class Meta:
        db_table = 'prescription_medicines'


class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # Ví dụ: "Tiền mặt", "Chuyển khoản", "Momo"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'payment_methods'
# Hóa đơn thanh toán
class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    pharmacist_id = models.CharField(max_length=50)
    totals = models.IntegerField()
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, help_text="Đơn thuốc được thanh toán")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, help_text="Phương thức thanh toán")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Thời gian tạo hóa đơn")
    image = models.TextField(blank=True,null=True)
    def __str__(self):
        return f"Hóa đơn #{self.id} - Đơn thuốc #{self.prescription.id}"

    class Meta:
        db_table = 'invoices'
        

