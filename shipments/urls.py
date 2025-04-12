from django.urls import path
from . import views

app_name = 'shipments'

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('create/', views.create_shipment, name='create_shipment'),
    path('<int:shipment_id>/', views.shipment_detail, name='shipment_detail'),
    path('<int:shipment_id>/update/', views.update_shipment, name='update_shipment'),
    path('<int:shipment_id>/delete/', views.delete_shipment, name='delete_shipment'),
    path('<int:shipment_id>/invoice/', views.download_invoice, name='download_invoice'),
    path('track/', views.track_shipment, name='track_shipment'),
    path('admin/', views.admin_shipments, name='admin_shipments'),
    path('admin/<int:pk>/update-status/', views.update_status, name='update_status'),
    path('admin/<int:pk>/add-update/', views.add_update, name='add_update'),
] 