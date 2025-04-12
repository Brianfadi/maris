from django.urls import path
from . import views

app_name = 'warehouses'

urlpatterns = [
    path('', views.warehouse_list, name='warehouse_list'),
    path('add/', views.warehouse_add, name='warehouse_add'),
    path('<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('<int:pk>/edit/', views.warehouse_edit, name='warehouse_edit'),
    path('<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
    # Inventory management URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('inventory/<int:pk>/edit/', views.edit_inventory, name='edit_inventory'),
    path('inventory/<int:pk>/delete/', views.delete_inventory, name='delete_inventory'),
    path('inventory/movement-history/', views.movement_history, name='movement_history'),
    path('inventory/stock-alerts/', views.stock_alerts, name='stock_alerts'),
    path('inventory/value-report/', views.inventory_value_report, name='inventory_value_report'),
] 