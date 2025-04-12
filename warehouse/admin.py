from django.contrib import admin
from .models import Warehouse, Inventory

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'created_at')
    search_fields = ('name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'quantity', 'unit', 'created_at')
    list_filter = ('warehouse', 'created_at')
    search_fields = ('name', 'warehouse__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',) 