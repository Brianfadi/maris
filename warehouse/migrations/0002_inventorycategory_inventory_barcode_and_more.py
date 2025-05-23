# Generated by Django 5.0.2 on 2025-03-25 07:57

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Inventory Categories',
            },
        ),
        migrations.AddField(
            model_name='inventory',
            name='barcode',
            field=models.CharField(blank=True, help_text='Barcode or QR code data', max_length=100),
        ),
        migrations.AddField(
            model_name='inventory',
            name='expiration_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='maximum_stock',
            field=models.IntegerField(default=0, help_text='Maximum stock capacity', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='inventory',
            name='minimum_stock',
            field=models.IntegerField(default=0, help_text='Minimum stock level before alert', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='inventory',
            name='sku',
            field=models.CharField(blank=True, help_text='Stock Keeping Unit', max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='inventory',
            name='volume',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Volume per unit in cubic meters', max_digits=10),
        ),
        migrations.AddField(
            model_name='inventory',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Weight per unit in kg', max_digits=10),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='current_occupancy',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Current occupied space in cubic meters', max_digits=10),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_warehouses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='warehouse',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('maintenance', 'Under Maintenance')], default='active', max_length=20),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='quantity',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='inventory',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='warehouse.inventorycategory'),
        ),
        migrations.CreateModel(
            name='InventoryMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_type', models.CharField(choices=[('transfer', 'Transfer'), ('receipt', 'Receipt'), ('adjustment', 'Adjustment'), ('return', 'Return')], max_length=20)),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('reference_number', models.CharField(max_length=50, unique=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('destination_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_movements', to='warehouse.warehouse')),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movements', to='warehouse.inventory')),
                ('source_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_movements', to='warehouse.warehouse')),
            ],
        ),
    ]
