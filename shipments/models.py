from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import time
import random
import string

User = get_user_model()

class Shipment(models.Model):
    """Model for tracking shipments in the logistics system."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('booked', 'Booked'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed_delivery', 'Failed Delivery'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
        ('customs_clearance', 'Customs Clearance'),
        ('exception', 'Exception'),
    ]
    
    SHIPMENT_TYPE_CHOICES = [
        ('air', 'Air Freight'),
        ('sea', 'Sea Freight'),
        ('land', 'Land Transport'),
        ('courier', 'Courier Service'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('mpesa', 'M-PESA'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    tracking_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Sender Information
    sender_name = models.CharField(max_length=100, blank=True, null=True)
    sender_email = models.EmailField(blank=True, null=True)
    sender_phone = models.CharField(max_length=20, blank=True, null=True)
    origin = models.CharField(max_length=200)
    
    # Receiver Information
    receiver_name = models.CharField(max_length=100, blank=True, null=True)
    receiver_email = models.EmailField(blank=True, null=True)
    receiver_phone = models.CharField(max_length=20, blank=True, null=True)
    destination = models.CharField(max_length=200)
    
    # Shipment Details
    shipment_type = models.CharField(max_length=20, choices=SHIPMENT_TYPE_CHOICES)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField()
    
    # New Fields
    quantity = models.PositiveIntegerField(default=1)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES)
    carrier = models.CharField(max_length=100)
    product = models.CharField(max_length=100)
    
    # Dates
    pickup_date = models.DateTimeField(default=timezone.now)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    
    # Status and Additional Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    additional_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.tracking_number or 'No Tracking Number'} - {self.get_status_display()}"
    
    def generate_tracking_number(self):
        """Generate a unique tracking number for the shipment"""
        prefix = {
            'air': 'AIR',
            'sea': 'SEA',
            'land': 'LND',
            'courier': 'CRR'
        }.get(self.shipment_type, 'GEN')
        
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}{timestamp}{random_str}"

    @property
    def status_color(self):
        """Return Bootstrap color class based on status"""
        colors = {
            'pending': 'warning',
            'in_transit': 'info',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return colors.get(self.status, 'secondary')
    
    class Meta:
        ordering = ['-created_at']

class ShipmentUpdate(models.Model):
    """Model for tracking individual updates/events in a shipment's journey."""
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='updates')
    status = models.CharField(max_length=20, choices=Shipment.STATUS_CHOICES)
    location = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} at {self.location}"
    
    class Meta:
        ordering = ['-timestamp'] 