from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, F, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.http import JsonResponse
from .models import Inventory, Warehouse, InventoryCategory, InventoryMovement
import uuid
from decimal import Decimal

def is_warehouse_staff(user):
    """Check if user is warehouse staff or admin."""
    return user.is_staff or hasattr(user, 'managed_warehouses')

@login_required
@user_passes_test(is_warehouse_staff)
def update_alert_settings(request):
    """Update warehouse alert settings."""
    if request.method == 'POST':
        try:
            # Get settings from POST data
            low_stock_threshold = float(request.POST.get('low_stock_threshold', 0))
            expiration_threshold = int(request.POST.get('expiration_threshold', 30))
            overstock_threshold = float(request.POST.get('overstock_threshold', 0))
            
            # Store settings in session (you might want to store these in a database model instead)
            request.session['warehouse_settings'] = {
                'low_stock_threshold': low_stock_threshold,
                'expiration_threshold': expiration_threshold,
                'overstock_threshold': overstock_threshold,
            }
            
            messages.success(request, 'Alert settings updated successfully.')
            return redirect('warehouse:stock_alerts')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    # Get current settings from session
    settings = request.session.get('warehouse_settings', {
        'low_stock_threshold': 0,
        'expiration_threshold': 30,
        'overstock_threshold': 0,
    })
    
    return render(request, 'warehouse/stock_alerts.html', {'settings': settings})

@login_required
@user_passes_test(is_warehouse_staff)
def warehouse_list(request):
    """Display list of warehouses."""
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse/warehouse_list.html', {'warehouses': warehouses})

@login_required
@user_passes_test(is_warehouse_staff)
def warehouse_detail(request, pk):
    """Display detailed information about a specific warehouse."""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    inventory = Inventory.objects.filter(warehouse=warehouse)
    return render(request, 'warehouse/warehouse_detail.html', {
        'warehouse': warehouse,
        'inventory': inventory
    })

@login_required
@user_passes_test(is_warehouse_staff)
def inventory_list(request):
    """Display list of all inventory items."""
    inventory = Inventory.objects.all()
    return render(request, 'warehouse/inventory_list.html', {'inventory': inventory})

@login_required
@user_passes_test(is_warehouse_staff)
def add_inventory(request):
    """Add new inventory item."""
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'warehouse/add_inventory.html')

@login_required
@user_passes_test(is_warehouse_staff)
def create_movement(request):
    """Create new inventory movement."""
    if request.method == 'POST':
        try:
            # Get form data
            movement_type = request.POST.get('movement_type')
            source_warehouse_id = request.POST.get('source_warehouse')
            destination_warehouse_id = request.POST.get('destination_warehouse')
            item_id = request.POST.get('item')
            quantity = int(request.POST.get('quantity'))
            notes = request.POST.get('notes')
            
            # Get the item
            item = Inventory.objects.get(id=item_id)
            
            # Validate movement
            if movement_type != 'receipt' and quantity > item.quantity:
                messages.error(request, 'Insufficient stock available')
                return redirect('warehouse:create_movement')
            
            # Create movement record
            movement = InventoryMovement.objects.create(
                reference_number=f"MOV-{uuid.uuid4().hex[:8].upper()}",
                movement_type=movement_type,
                inventory=item,
                quantity=quantity,
                source_warehouse_id=source_warehouse_id,
                destination_warehouse_id=destination_warehouse_id,
                notes=notes,
                created_by=request.user
            )
            
            # Update inventory quantities
            if movement_type == 'transfer':
                # Decrease from source
                item.quantity -= quantity
                item.save()
                
                # Create or update destination item
                dest_item, created = Inventory.objects.get_or_create(
                    item=item.item,
                    warehouse_id=destination_warehouse_id,
                    defaults={
                        'unit_price': item.unit_price,
                        'minimum_stock': item.minimum_stock,
                        'maximum_stock': item.maximum_stock,
                        'location': item.location,
                        'category': item.category
                    }
                )
                dest_item.quantity += quantity
                dest_item.save()
                
            elif movement_type == 'receipt':
                # Increase quantity
                item.quantity += quantity
                item.save()
                
            elif movement_type == 'issue':
                # Decrease quantity
                item.quantity -= quantity
                item.save()
            
            messages.success(request, 'Movement created successfully')
            return redirect('warehouse:movement_history')
            
        except Exception as e:
            messages.error(request, f'Error creating movement: {str(e)}')
            return redirect('warehouse:create_movement')
    
    # Generate reference number
    reference_number = f"MOV-{uuid.uuid4().hex[:8].upper()}"
    
    # Get context data
    context = {
        'warehouses': Warehouse.objects.all(),
        'inventory': Inventory.objects.all(),
        'reference_number': reference_number,
        'recent_movements': InventoryMovement.objects.select_related('inventory').order_by('-created_at')[:5]
    }
    
    return render(request, 'warehouse/create_movement.html', context)

@login_required
@user_passes_test(is_warehouse_staff)
def movement_history(request):
    """Display inventory movement history."""
    movements = InventoryMovement.objects.all()
    return render(request, 'warehouse/movement_history.html', {'movements': movements})

@login_required
@user_passes_test(is_warehouse_staff)
def stock_alerts(request):
    """Display stock alerts for low inventory and expired items."""
    # Get settings from session
    settings = request.session.get('warehouse_settings', {
        'low_stock_threshold': 20,  # Default 20% below minimum
        'near_low_stock_threshold': 10,  # Default 10% above minimum
        'expiry_warning_days': 30,  # Default 30 days
        'overstock_threshold': 10,  # Default 10% above maximum
        'email_notifications': False,
        'auto_reorder': False,
    })
    
    # Get warehouses and categories for filters
    warehouses = Warehouse.objects.all()
    categories = InventoryCategory.objects.all()
    
    # Get low stock items
    low_stock_items = Inventory.objects.filter(
        quantity__lte=F('minimum_stock') * (1 + settings['low_stock_threshold'] / 100)
    )
    
    # Get near low stock items
    near_low_stock_items = Inventory.objects.filter(
        quantity__gt=F('minimum_stock'),
        quantity__lte=F('minimum_stock') * (1 + settings['near_low_stock_threshold'] / 100)
    )
    
    # Get items expiring soon
    expiration_date = timezone.now().date() + timezone.timedelta(days=settings['expiry_warning_days'])
    expiring_items = Inventory.objects.filter(
        expiration_date__lte=expiration_date,
        expiration_date__gt=timezone.now().date()
    )
    
    # Get overstocked items
    overstocked_items = Inventory.objects.filter(
        quantity__gte=F('maximum_stock') * (1 + settings['overstock_threshold'] / 100)
    )
    
    # Prepare alerts list
    alerts = []
    
    # Add low stock alerts
    for item in low_stock_items:
        alerts.append({
            'inventory': item,
            'type': 'low_stock',
            'severity': 'high',
            'value_at_risk': (item.minimum_stock - item.quantity) * item.unit_price,
            'recommended_reorder': item.minimum_stock * 2 - item.quantity
        })
    
    # Add near low stock alerts
    for item in near_low_stock_items:
        alerts.append({
            'inventory': item,
            'type': 'near_low_stock',
            'severity': 'medium',
            'value_at_risk': 0,
            'recommended_reorder': item.minimum_stock - item.quantity
        })
    
    # Add expiring items alerts
    for item in expiring_items:
        days_until_expiry = (item.expiration_date - timezone.now().date()).days
        alerts.append({
            'inventory': item,
            'type': 'expiring_soon',
            'severity': 'medium' if days_until_expiry > 7 else 'high',
            'value_at_risk': item.quantity * item.unit_price,
            'days_until_expiry': days_until_expiry
        })
    
    # Add overstocked alerts
    for item in overstocked_items:
        alerts.append({
            'inventory': item,
            'type': 'overstocked',
            'severity': 'low',
            'value_at_risk': (item.quantity - item.maximum_stock) * item.unit_price,
            'recommended_transfer': item.quantity - item.maximum_stock
        })
    
    # Sort alerts by severity and value at risk
    alerts.sort(key=lambda x: (-len(x['severity']), -x.get('value_at_risk', 0)))
    
    context = {
        'settings': settings,
        'warehouses': warehouses,
        'categories': categories,
        'alerts': alerts,
        'low_stock_count': len(low_stock_items),
        'near_low_stock_count': len(near_low_stock_items),
        'expiring_soon_count': len(expiring_items),
        'overstocked_count': len(overstocked_items),
    }
    return render(request, 'warehouse/stock_alerts.html', context)


@login_required
@user_passes_test(is_warehouse_staff)
def inventory_value_report(request):
    """Generate inventory value report."""
    # Calculate total inventory value
    total_value = Inventory.objects.aggregate(
        total_value=Sum(F('quantity') * F('unit_price'))
    )['total_value'] or 0

    # Get value by category with percentages
    value_by_category = []
    category_values = Inventory.objects.values('category__name').annotate(
        total_value=Sum(F('quantity') * F('unit_price'))
    )
    for category in category_values:
        category['percentage'] = (category['total_value'] / total_value * 100) if total_value > 0 else 0
        value_by_category.append(category)

    # Get value by warehouse with percentages
    value_by_warehouse = []
    warehouse_values = Inventory.objects.values('warehouse__name').annotate(
        total_value=Sum(F('quantity') * F('unit_price'))
    )
    for warehouse in warehouse_values:
        warehouse['percentage'] = (warehouse['total_value'] / total_value * 100) if total_value > 0 else 0
        value_by_warehouse.append(warehouse)

    # Get high value items (top 10 by total value)
    high_value_items = Inventory.objects.annotate(
        total_value=F('quantity') * F('unit_price')
    ).order_by('-total_value')[:10]

    context = {
        'total_value': total_value,
        'value_by_category': value_by_category,
        'value_by_warehouse': value_by_warehouse,
        'high_value_items': high_value_items,
        'today': timezone.now(),
    }
    return render(request, 'warehouse/inventory_value_report.html', context)