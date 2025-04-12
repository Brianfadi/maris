# Generated by Django 5.0.2 on 2025-03-24 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0003_remove_shipment_dimensions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('booked', 'Booked'), ('picked_up', 'Picked Up'), ('in_transit', 'In Transit'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('failed_delivery', 'Failed Delivery'), ('returned', 'Returned'), ('cancelled', 'Cancelled'), ('on_hold', 'On Hold'), ('customs_clearance', 'Customs Clearance'), ('exception', 'Exception')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='shipmentupdate',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('booked', 'Booked'), ('picked_up', 'Picked Up'), ('in_transit', 'In Transit'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('failed_delivery', 'Failed Delivery'), ('returned', 'Returned'), ('cancelled', 'Cancelled'), ('on_hold', 'On Hold'), ('customs_clearance', 'Customs Clearance'), ('exception', 'Exception')], max_length=20),
        ),
    ]
