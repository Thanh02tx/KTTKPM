# Generated by Django 3.2 on 2025-05-08 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0006_auto_20250508_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='image',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
