from django.shortcuts import render
from .models import Service

# Create your views here.

def service_list(request):
    """Display list of all services."""
    services = Service.objects.filter(is_active=True).order_by('name')
    context = {
        'services': services,
        'page_title': 'Our Services',
        'page_description': 'Comprehensive logistics solutions tailored to your business needs'
    }
    return render(request, 'services/service_list.html', context)

def sea_freight(request):
    """Sea freight service page."""
    return render(request, 'services/sea_freight.html')

def courier(request):
    """Courier service page."""
    return render(request, 'services/courier.html')

def airfreight(request):
    """Airfreight service page."""
    return render(request, 'services/airfreight.html')

def customs_clearance(request):
    """Customs clearance service page."""
    return render(request, 'services/customs_clearance.html')

def e_commerce(request):
    """E-commerce service page."""
    return render(request, 'services/e_commerce.html')

def ecommerce(request):
    return render(request, 'services/ecommerce.html')
