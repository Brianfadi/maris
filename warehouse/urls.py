from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    # Warehouse URLs
    path('', views.warehouse_list, name='warehouse_list'),
    path('<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    
    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    
    # Inventory Movement URLs
    path('movement/create/', views.create_movement, name='create_movement'),
    path('movement/history/', views.movement_history, name='movement_history'),
    
    # Reports and Alerts
    path('alerts/', views.stock_alerts, name='stock_alerts'),
    path('alerts/settings/', views.update_alert_settings, name='update_alert_settings'),
    path('reports/value/', views.inventory_value_report, name='inventory_value_report'),
] 