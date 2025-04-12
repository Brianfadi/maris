from django.contrib import admin
from .models import CustomerProfile, CustomerDocument

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_registration_number', 'tax_id', 'created_at')
    search_fields = ('user__email', 'company_registration_number', 'tax_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('customer__user__email', 'document_type')
    readonly_fields = ('uploaded_at',)
    ordering = ('-uploaded_at',) 