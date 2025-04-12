from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, ExpressionWrapper, DecimalField, Sum, Avg
from django.core.paginator import Paginator
from datetime import datetime
from .models import Warehouse, InventoryMovement, InventoryItem
from .forms import WarehouseForm, InventoryItemForm
from .decorators import staff_required

# Create your views here.

@login_required
@staff_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    total_capacity = sum(warehouse.capacity for warehouse in warehouses)
    total_occupancy = sum(warehouse.current_occupancy for warehouse in warehouses)
    available_space = total_capacity - total_occupancy
    active_warehouses = warehouses.filter(is_active=True).count()
    
    context = {
        'warehouses': warehouses,
        'total_capacity': total_capacity,
        'total_occupancy': total_occupancy,
        'available_space': available_space,
        'active_warehouses': active_warehouses,
    }
    return render(request, 'warehouses/warehouse_list.html', context)

@login_required
@staff_required
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    return render(request, 'warehouses/warehouse_detail.html', {'warehouse': warehouse})

@login_required
@staff_required
def warehouse_add(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'Warehouse "{warehouse.name}" was created successfully.')
            return redirect('warehouses:warehouse_list')
    else:
        form = WarehouseForm()
    
    return render(request, 'warehouses/warehouse_form.html', {'form': form})

@login_required
@staff_required
def warehouse_edit(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'Warehouse "{warehouse.name}" was updated successfully.')
            return redirect('warehouses:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm(instance=warehouse)
    
    return render(request, 'warehouses/warehouse_form.html', {'form': form, 'warehouse': warehouse})

@login_required
@staff_required
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse_name = warehouse.name
        warehouse.delete()
        messages.success(request, f'Warehouse "{warehouse_name}" was deleted successfully.')
        return redirect('warehouses:warehouse_list')
    
    return render(request, 'warehouses/warehouse_confirm_delete.html', {'warehouse': warehouse})

# Inventory Management Views
@login_required
def inventory_list(request):
    # Get filter parameters
    warehouse_id = request.GET.get('warehouse')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)

    # Get all warehouses for the filter dropdown
    warehouses = Warehouse.objects.all()

    # Start with all inventory items
    items = InventoryItem.objects.select_related('warehouse').all()

    # Apply filters
    if warehouse_id:
        items = items.filter(warehouse_id=warehouse_id)

    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    # Calculate summary statistics
    total_items = items.count()
    total_value = items.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0
    avg_price = items.aggregate(
        avg=Avg('unit_price')
    )['avg'] or 0
    low_stock_count = items.filter(
        quantity__lte=F('low_stock_threshold')
    ).count()

    # Order by name
    items = items.order_by('name')

    # Paginate the results
    paginator = Paginator(items, 25)  # Show 25 items per page
    items = paginator.get_page(page)

    context = {
        'items': items,
        'warehouses': warehouses,
        'selected_warehouse': int(warehouse_id) if warehouse_id else None,
        'search_query': search_query,
        'total_items': total_items,
        'total_value': total_value,
        'avg_price': avg_price,
        'low_stock_count': low_stock_count,
    }

    return render(request, 'warehouses/inventory_list.html', context)

@login_required
def add_inventory(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Inventory item "{item.name}" was created successfully.')
            return redirect('warehouses:inventory_list')
    else:
        form = InventoryItemForm()
    
    return render(request, 'warehouses/add_inventory.html', {'form': form})

@login_required
def movement_history(request):
    # Get filter parameters
    warehouse_id = request.GET.get('warehouse')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    movement_type = request.GET.get('movement_type')
    page = request.GET.get('page', 1)

    # Get all warehouses for the filter dropdown
    warehouses = Warehouse.objects.all()

    # Start with all movements
    movements = InventoryMovement.objects.all().order_by('-date')

    # Apply filters
    if warehouse_id:
        movements = movements.filter(
            Q(from_warehouse_id=warehouse_id) | Q(to_warehouse_id=warehouse_id)
        )

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            movements = movements.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            movements = movements.filter(date__lte=end_date)
        except ValueError:
            pass

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    # Paginate the results
    paginator = Paginator(movements, 25)  # Show 25 movements per page
    movements = paginator.get_page(page)

    context = {
        'movements': movements,
        'warehouses': warehouses,
        'selected_warehouse': int(warehouse_id) if warehouse_id else None,
        'start_date': start_date,
        'end_date': end_date,
        'movement_type': movement_type,
    }

    return render(request, 'warehouses/movement_history.html', context)

@login_required
def stock_alerts(request):
    # Get filter parameters
    warehouse_id = request.GET.get('warehouse')
    alert_type = request.GET.get('alert_type', 'all')
    page = request.GET.get('page', 1)

    # Get all warehouses for the filter dropdown
    warehouses = Warehouse.objects.all()

    # Get all inventory items with their quantities
    inventory_items = InventoryItem.objects.all()
    
    # Define thresholds (you might want to make these configurable)
    low_stock_threshold = 10  # Alert when quantity is below 10
    overstock_threshold = 90  # Alert when occupancy is above 90%

    # Get warehouses with high occupancy
    # Calculate occupancy percentage using database fields
    warehouses = Warehouse.objects.annotate(
        calc_occupancy_pct=ExpressionWrapper(
            (F('current_occupancy') * 100.0) / F('capacity'),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    ).filter(is_active=True)

    if alert_type == 'overstock':
        warehouses = warehouses.filter(calc_occupancy_pct__gte=overstock_threshold)
    elif alert_type == 'low_stock':
        warehouses = warehouses.filter(calc_occupancy_pct__lt=low_stock_threshold)

    if warehouse_id:
        warehouses = warehouses.filter(id=warehouse_id)

    # Order by occupancy percentage descending
    warehouses = warehouses.order_by('-calc_occupancy_pct')

    # Paginate the results
    paginator = Paginator(warehouses, 10)  # Show 10 alerts per page
    alerts = paginator.get_page(page)

    context = {
        'warehouses': warehouses,
        'selected_warehouse': int(warehouse_id) if warehouse_id else None,
        'alert_type': alert_type,
        'alerts': alerts,
        'low_stock_threshold': low_stock_threshold,
        'overstock_threshold': overstock_threshold,
    }

    return render(request, 'warehouses/stock_alerts.html', context)

@login_required
def inventory_value_report(request):
    # Get filter parameters
    warehouse_id = request.GET.get('warehouse')
    page = request.GET.get('page', 1)

    # Get all warehouses for the filter dropdown
    warehouses = Warehouse.objects.all()

    # Calculate inventory value for each warehouse
    # Using a fixed value of $100 per unit for demonstration
    VALUE_PER_UNIT = 100
    
    warehouse_values = Warehouse.objects.annotate(
        total_value=ExpressionWrapper(
            F('current_occupancy') * VALUE_PER_UNIT,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        calc_occupancy_pct=ExpressionWrapper(
            (F('current_occupancy') * 100.0) / F('capacity'),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    ).filter(is_active=True)

    if warehouse_id:
        warehouse_values = warehouse_values.filter(id=warehouse_id)

    # Calculate total inventory value
    total_value = warehouse_values.aggregate(
        total=Sum('total_value')
    )['total'] or 0

    # Order by value descending
    warehouse_values = warehouse_values.order_by('-total_value')

    # Paginate the results
    paginator = Paginator(warehouse_values, 10)  # Show 10 warehouses per page
    values = paginator.get_page(page)

    context = {
        'warehouses': warehouses,
        'selected_warehouse': int(warehouse_id) if warehouse_id else None,
        'values': values,
        'total_value': total_value,
    }

    return render(request, 'warehouses/inventory_value_report.html', context)

@login_required
def edit_inventory(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Inventory item "{item.name}" was updated successfully.')
            return redirect('warehouses:inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    
    return render(request, 'warehouses/add_inventory.html', {'form': form})

@login_required
def delete_inventory(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'Inventory item "{item_name}" was deleted successfully.')
        return redirect('warehouses:inventory_list')
    
    return render(request, 'warehouses/delete_inventory.html', {'item': item})
