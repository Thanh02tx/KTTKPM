# Generated by Django 5.2 on 2025-04-18 14:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_doctor_gender_alter_doctor_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cashier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.TextField()),
                ('name', models.CharField(max_length=500)),
                ('gender', models.CharField(choices=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')], max_length=10)),
                ('phone', models.CharField(max_length=15)),
                ('date_of_birth', models.DateField()),
                ('province', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('ward', models.CharField(blank=True, max_length=100, null=True)),
                ('address_detail', models.CharField(max_length=255)),
                ('bio_html', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cashiers',
            },
        ),
    ]
