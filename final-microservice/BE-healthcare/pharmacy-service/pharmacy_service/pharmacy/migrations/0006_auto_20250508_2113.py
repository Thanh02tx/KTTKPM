# Generated by Django 3.2 on 2025-05-08 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0005_auto_20250507_2134'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'payment_methods',
            },
        ),
        migrations.AlterField(
            model_name='prescription',
            name='status',
            field=models.CharField(choices=[('pending', 'Chờ bán thuốc'), ('sold', 'Đã bán xong')], default='pending', help_text='Trạng thái đơn thuốc', max_length=50),
        ),
        migrations.AddField(
            model_name='invoice',
            name='payment_method',
            field=models.ForeignKey(blank=True, help_text='Phương thức thanh toán', null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmacy.paymentmethod'),
        ),
    ]
