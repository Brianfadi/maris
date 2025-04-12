from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('sea-freight/', views.sea_freight, name='sea_freight'),
    path('courier/', views.courier, name='courier'),
    path('airfreight/', views.airfreight, name='airfreight'),
    path('customs-clearance/', views.customs_clearance, name='customs_clearance'),
    path('e-commerce/', views.ecommerce, name='ecommerce'),
] 