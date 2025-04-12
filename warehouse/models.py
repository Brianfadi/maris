from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Warehouse(models.Model):
    """Model for managing warehouses in the logistics system."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacity in cubic meters")
    current_occupancy = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Current occupied space in cubic meters")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Contact Information
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_warehouses')
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_occupancy_percentage(self):
        """Calculate the warehouse occupancy percentage."""
        if self.capacity:
            return (self.current_occupancy / self.capacity) * 100
        return 0
    
    def get_available_space(self):
        """Calculate available space in the warehouse."""
        return self.capacity - self.current_occupancy
    
    def has_available_space(self, required_space):
        """Check if warehouse has available space for the required amount."""
        return (self.current_occupancy + Decimal(str(required_space))) <= self.capacity

class InventoryCategory(models.Model):
    """Model for categorizing inventory items."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Inventory Categories"

class Inventory(models.Model):
    """Model for tracking inventory items in warehouses."""
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory')
    category = models.ForeignKey(InventoryCategory, on_delete=models.SET_NULL, null=True, related_name='items')
    
    # Basic Information
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Stock Keeping Unit")
    barcode = models.CharField(max_length=100, blank=True, help_text="Barcode or QR code data")
    description = models.TextField(blank=True)
    
    # Stock Information
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20)
    minimum_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Minimum stock level before alert")
    maximum_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Maximum stock capacity")
    
    # Dimensions and Space
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Weight per unit in kg")
    volume = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Volume per unit in cubic meters")
    
    # Financial Information
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Dates
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.warehouse.name}"
    
    def get_total_value(self):
        """Calculate total value of inventory item."""
        return self.quantity * self.unit_price
    
    def get_total_volume(self):
        """Calculate total volume of inventory item."""
        return self.quantity * self.volume
    
    def is_low_stock(self):
        """Check if inventory is below minimum stock level."""
        return self.quantity <= self.minimum_stock
    
    def is_expired(self):
        """Check if inventory item is expired."""
        if self.expiration_date:
            return self.expiration_date <= timezone.now().date()
        return False

class InventoryMovement(models.Model):
    """Model for tracking inventory movements between warehouses."""
    
    MOVEMENT_TYPES = [
        ('transfer', 'Transfer'),
        ('receipt', 'Receipt'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    ]
    
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='movements')
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outgoing_movements')
    destination_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='incoming_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Movement Information
    reference_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    
    # User and Timestamps
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.movement_type} - {self.reference_number}"
    
    def complete_movement(self):
        """Complete the inventory movement and update warehouse occupancy."""
        if not self.completed_at:
            # Update source warehouse
            self.inventory.quantity -= self.quantity
            self.source_warehouse.current_occupancy -= (self.quantity * self.inventory.volume)
            
            # Update destination warehouse
            self.destination_warehouse.current_occupancy += (self.quantity * self.inventory.volume)
            
            # Save changes
            self.inventory.save()
            self.source_warehouse.save()
            self.destination_warehouse.save()
            
            # Mark movement as completed
            self.completed_at = timezone.now()
            self.save() 