# Generated by Django 5.0.2 on 2025-03-24 14:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='additional_details',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='pickup_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='receiver_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='receiver_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='receiver_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='sender_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='sender_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='sender_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='dimensions',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('picked_up', 'Picked Up'), ('in_transit', 'In Transit'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='tracking_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='shipmentupdate',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='shipmentupdate',
            name='shipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipmentupdates', to='shipments.shipment'),
        ),
        migrations.AlterField(
            model_name='shipmentupdate',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('picked_up', 'Picked Up'), ('in_transit', 'In Transit'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], max_length=20),
        ),
    ]
