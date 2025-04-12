from django import forms
from .models import Warehouse, InventoryItem

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'capacity', 'is_active']

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'description', 'sku', 'unit_price', 'quantity', 'warehouse', 'low_stock_threshold']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        warehouse = cleaned_data.get('warehouse')

        if warehouse and quantity:
            # Check if there's enough space in the warehouse
            available_space = warehouse.available_space
            if quantity > available_space:
                raise forms.ValidationError(
                    f"Not enough space in warehouse. Available space: {available_space}"
                )

        return cleaned_data 