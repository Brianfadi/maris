from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Shipment, ShipmentUpdate
import uuid
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import Context, Template
from django.template.loader import get_template
from django.template import Library
from django.conf import settings
import os
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from .forms import ShipmentForm, ShipmentUpdateForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

register = Library()

def is_staff(user):
    return user.is_staff

@login_required(login_url='accounts:login')
def shipment_list(request):
    shipments = Shipment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shipments/shipment_list.html', {'shipments': shipments})

@login_required
def shipment_detail(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    
    # Check if the user is the owner of the shipment
    if shipment.user != request.user:
        messages.error(request, "You don't have permission to view this shipment.")
        return redirect('shipments:shipment_list')
    
    # Get all updates for this shipment, ordered by timestamp
    updates = ShipmentUpdate.objects.filter(shipment=shipment).order_by('-timestamp')
    
    # Get the latest update
    latest_update = updates.first() if updates else None
    
    context = {
        'shipment': shipment,
        'updates': updates,
        'latest_update': latest_update,
    }
    
    return render(request, 'shipments/shipment_detail.html', context)

@login_required
def create_shipment(request):
    if request.method == 'POST':
        try:
            # Get form data
            form_data = {
                'sender_name': request.POST.get('sender_name'),
                'sender_email': request.POST.get('sender_email'),
                'sender_phone': request.POST.get('sender_phone'),
                'origin': request.POST.get('origin'),
                'receiver_name': request.POST.get('receiver_name'),
                'receiver_email': request.POST.get('receiver_email'),
                'receiver_phone': request.POST.get('receiver_phone'),
                'destination': request.POST.get('destination'),
                'shipment_type': request.POST.get('shipment_type'),
                'weight': request.POST.get('weight'),
                'product': request.POST.get('product'),
                'quantity': request.POST.get('quantity'),
                'payment_mode': request.POST.get('payment_mode'),
                'carrier': request.POST.get('carrier'),
                'description': request.POST.get('description'),
                'pickup_date': request.POST.get('pickup_date'),
                'estimated_delivery': request.POST.get('estimated_delivery'),
                'additional_details': request.POST.get('additional_details'),
            }

            # Validate required fields
            required_fields = [
                'sender_name', 'sender_email', 'sender_phone', 'origin',
                'receiver_name', 'receiver_email', 'receiver_phone', 'destination',
                'shipment_type', 'weight', 'product', 'quantity',
                'payment_mode', 'carrier', 'pickup_date'
            ]

            missing_fields = [field for field in required_fields if not form_data[field]]
            if missing_fields:
                messages.error(request, f'Please fill in all required fields: {", ".join(missing_fields)}')
                return render(request, 'shipments/create_shipment.html', {'form_data': form_data})

            # Create shipment without tracking number
            shipment = Shipment.objects.create(
                user=request.user,
                **form_data
            )

            # Create initial shipment update
            ShipmentUpdate.objects.create(
                shipment=shipment,
                status='pending',
                location=shipment.origin,
                description='Shipment created and pending processing'
            )

            messages.success(request, 'Shipment created successfully! You will receive a tracking number soon.')
            return redirect('shipments:shipment_list')

        except Exception as e:
            messages.error(request, f'Error creating shipment: {str(e)}')
            return render(request, 'shipments/create_shipment.html', {'form_data': form_data})

    return render(request, 'shipments/create_shipment.html')

@login_required(login_url='accounts:login')
def track_shipment(request):
    tracking_number = request.GET.get('tracking_number')
    shipment = None
    error_message = None
    
    if tracking_number:
        try:
            shipment = Shipment.objects.filter(
                tracking_number=tracking_number
            ).first()
            
            if not shipment:
                error_message = "No shipment found with this tracking number."
            elif shipment.user != request.user and not request.user.is_staff:
                # If the shipment exists but belongs to another user,
                # only show basic tracking info
                shipment.hide_sensitive_info = True
                
        except Exception as e:
            error_message = "An error occurred while tracking the shipment."
    
    return render(request, 'shipments/track_shipment.html', {
        'shipment': shipment,
        'error_message': error_message,
        'tracking_number': tracking_number
    })

@user_passes_test(is_staff, login_url='accounts:login')
def admin_shipments(request):
    search = request.GET.get('search', '')
    if search:
        shipments = Shipment.objects.filter(tracking_number__icontains=search).order_by('-created_at')
    else:
        shipments = Shipment.objects.all().order_by('-created_at')
    
    return render(request, 'shipments/admin_shipments.html', {
        'shipments': shipments
    })

@user_passes_test(is_staff, login_url='accounts:login')
def update_status(request, pk):
    if request.method == 'POST':
        shipment = get_object_or_404(Shipment, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status and new_status in dict(Shipment.STATUS_CHOICES):
            old_status = shipment.status
            shipment.status = new_status
            
            # If status is changed to delivered, set actual delivery date
            if new_status == 'delivered' and old_status != 'delivered':
                shipment.actual_delivery = timezone.now()
            elif new_status != 'delivered':
                shipment.actual_delivery = None
                
            shipment.save()
            
            # Create a shipment update
            ShipmentUpdate.objects.create(
                shipment=shipment,
                status=new_status,
                location=shipment.destination if new_status == 'delivered' else shipment.origin,
                description=f'Status updated to {dict(Shipment.STATUS_CHOICES)[new_status]}'
            )
            
            messages.success(request, 'Shipment status updated successfully.')
        else:
            messages.error(request, 'Invalid status provided.')
    
    return redirect('shipments:admin_shipments')

@user_passes_test(is_staff, login_url='accounts:login')
def add_update(request, pk):
    if request.method == 'POST':
        shipment = get_object_or_404(Shipment, pk=pk)
        status = request.POST.get('status')
        location = request.POST.get('location')
        description = request.POST.get('description')
        
        if status and location:
            # Update shipment status
            if status in dict(Shipment.STATUS_CHOICES):
                old_status = shipment.status
                shipment.status = status
                
                # If status is changed to delivered, set actual delivery date
                if status == 'delivered' and old_status != 'delivered':
                    shipment.actual_delivery = timezone.now()
                elif status != 'delivered':
                    shipment.actual_delivery = None
                    
                shipment.save()
            
            # Create shipment update
            ShipmentUpdate.objects.create(
                shipment=shipment,
                status=status,
                location=location,
                description=description
            )
            
            messages.success(request, 'Shipment update added successfully.')
        else:
            messages.error(request, 'Status and location are required.')
    
    return redirect('shipments:admin_shipments')

@login_required
def update_shipment(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    
    if request.method == 'POST':
        form = ShipmentUpdateForm(request.POST, instance=shipment)
        if form.is_valid():
            # Only allow tracking number assignment if user is staff
            if request.user.is_staff:
                tracking_number = form.cleaned_data.get('tracking_number')
                if tracking_number:
                    shipment.tracking_number = tracking_number
                elif not shipment.tracking_number:
                    # Generate tracking number if not assigned
                    shipment.tracking_number = shipment.generate_tracking_number()
            
            shipment = form.save()
            
            # Create shipment update
            ShipmentUpdate.objects.create(
                shipment=shipment,
                status=shipment.status,
                location=form.cleaned_data.get('location', ''),
                description=form.cleaned_data.get('description', '')
            )
            
            messages.success(request, 'Shipment updated successfully.')
            return redirect('shipments:shipment_detail', pk=shipment.pk)
    else:
        form = ShipmentUpdateForm(instance=shipment)
    
    return render(request, 'shipments/update_shipment.html', {
        'form': form,
        'shipment': shipment
    })

@register.filter
def multiply(value, arg):
    return value * arg

@login_required
def download_invoice(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id, user=request.user)
    
    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    # Add title
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Paragraph("Maris Logistics Ltd", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Invoice details
    invoice_data = [
        ['Invoice Number:', shipment.tracking_number],
        ['Date:', shipment.created_at.strftime('%B %d, %Y')],
        ['Status:', shipment.get_status_display()],
        ['Payment Method:', shipment.get_payment_mode_display()],
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Sender Information
    elements.append(Paragraph("Sender Information", styles['Heading3']))
    sender_data = [
        ['Name:', shipment.sender_name],
        ['Email:', shipment.sender_email],
        ['Phone:', shipment.sender_phone],
        ['Origin:', shipment.origin],
    ]
    
    sender_table = Table(sender_data, colWidths=[2*inch, 4*inch])
    sender_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(sender_table)
    elements.append(Spacer(1, 20))
    
    # Receiver Information
    elements.append(Paragraph("Receiver Information", styles['Heading3']))
    receiver_data = [
        ['Name:', shipment.receiver_name],
        ['Email:', shipment.receiver_email],
        ['Phone:', shipment.receiver_phone],
        ['Destination:', shipment.destination],
    ]
    
    receiver_table = Table(receiver_data, colWidths=[2*inch, 4*inch])
    receiver_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(receiver_table)
    elements.append(Spacer(1, 20))
    
    # Shipment Details
    elements.append(Paragraph("Shipment Details", styles['Heading3']))
    shipment_data = [
        ['Type:', shipment.get_shipment_type_display()],
        ['Product:', shipment.product],
        ['Quantity:', str(shipment.quantity)],
        ['Weight:', f"{shipment.weight} kg"],
        ['Pickup Date:', shipment.pickup_date.strftime('%B %d, %Y')],
        ['Estimated Delivery:', shipment.estimated_delivery.strftime('%B %d, %Y') if shipment.estimated_delivery else 'N/A'],
        ['Carrier:', shipment.carrier],
    ]
    
    shipment_table = Table(shipment_data, colWidths=[2*inch, 4*inch])
    shipment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(shipment_table)
    elements.append(Spacer(1, 20))
    
    # Description
    elements.append(Paragraph("Description", styles['Heading3']))
    elements.append(Paragraph(shipment.description, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Total Amount
    total_amount = shipment.weight * 1000  # Assuming KES 1000 per kg
    elements.append(Paragraph(f"Total Amount: KES {total_amount:,.2f}", styles['Heading2']))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse object with the appropriate PDF headers
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{shipment.tracking_number}.pdf"'
    
    return response

@login_required
def delete_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    
    # Check if the user is the owner of the shipment
    if shipment.user != request.user:
        messages.error(request, "You don't have permission to delete this shipment.")
        return redirect('shipments:shipment_list')
    
    if request.method == 'POST':
        shipment.delete()
        messages.success(request, 'Shipment deleted successfully.')
        return redirect('shipments:shipment_list')
    
    return render(request, 'shipments/shipment_confirm_delete.html', {'shipment': shipment}) 