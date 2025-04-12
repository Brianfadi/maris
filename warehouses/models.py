from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_occupancy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

    @property
    def available_space(self):
        return self.capacity - self.current_occupancy

    @property
    def occupancy_percentage(self):
        if self.capacity > 0:
            return (self.current_occupancy / self.capacity) * 100
        return 0

    class Meta:
        ordering = ['-created_at']

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_items', null=True, blank=True)
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def total_value(self):
        return self.quantity * self.unit_price

    class Meta:
        ordering = ['name']

class InventoryMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Incoming'),
        ('out', 'Outgoing'),
        ('transfer', 'Transfer'),
    )

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, 
                                     related_name='outgoing_movements', null=True, blank=True)
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, 
                                   related_name='incoming_movements', null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='warehouse_movements')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.item.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # Update warehouse occupancy when movement is saved
        if self.movement_type == 'in' and self.to_warehouse:
            self.to_warehouse.current_occupancy += self.quantity
            self.to_warehouse.save()
        elif self.movement_type == 'out' and self.from_warehouse:
            self.from_warehouse.current_occupancy -= self.quantity
            self.from_warehouse.save()
        elif self.movement_type == 'transfer' and self.from_warehouse and self.to_warehouse:
            self.from_warehouse.current_occupancy -= self.quantity
            self.to_warehouse.current_occupancy += self.quantity
            self.from_warehouse.save()
            self.to_warehouse.save()
        
        super().save(*args, **kwargs)
