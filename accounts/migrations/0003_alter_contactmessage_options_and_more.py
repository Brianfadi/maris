# Generated by Django 5.0.2 on 2025-03-22 15:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_contactmessage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contactmessage',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_customer',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_staff_member',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='contactmessage',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='contactmessage',
            name='phone',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
