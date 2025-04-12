from django import forms
from .models import Shipment, ShipmentUpdate

class ShipmentUpdateForm(forms.ModelForm):
    location = forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    tracking_number = forms.CharField(max_length=20, required=False, 
                                    help_text="Leave blank to auto-generate")

    class Meta:
        model = ShipmentUpdate
        fields = ['status', 'location', 'description']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'sender_name', 'sender_email', 'sender_phone', 'origin',
            'receiver_name', 'receiver_email', 'receiver_phone', 'destination',
            'shipment_type', 'product', 'quantity', 'weight',
            'payment_mode', 'carrier', 'pickup_date', 'estimated_delivery',
            'description'
        ]
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sender_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sender_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'receiver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'receiver_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'receiver_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'shipment_type': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_mode': forms.Select(attrs={'class': 'form-control'}),
            'carrier': forms.Select(attrs={'class': 'form-control'}),
            'pickup_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estimated_delivery': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 