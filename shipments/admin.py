from django.contrib import admin
from .models import Shipment, ShipmentUpdate

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'user', 'origin', 'destination', 'status', 'created_at')
    list_filter = ('status', 'shipment_type', 'created_at')
    search_fields = ('tracking_number', 'user__email', 'origin', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(ShipmentUpdate)
class ShipmentUpdateAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'location', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('shipment__tracking_number', 'location', 'status')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',) 