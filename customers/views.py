from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomerProfile, CustomerDocument

@login_required
def customer_list(request):
    customers = CustomerProfile.objects.all()
    return render(request, 'customers/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    customer = CustomerProfile.objects.get(pk=pk)
    return render(request, 'customers/customer_detail.html', {'customer': customer})

@login_required
def add_customer(request):
    if request.method == 'POST':
        # Handle customer addition
        pass
    return render(request, 'customers/add_customer.html') 