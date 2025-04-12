from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomUser, ContactMessage, VerificationCode
from shipments.models import Shipment
from .forms import ContactForm, UserRegistrationForm, UserEditForm
from warehouses.models import Warehouse
from django.contrib.auth.models import User
from .utils import create_verification_code
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse

def home(request):
    """Home page view."""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('accounts:admin_dashboard')
    return render(request, 'home.html')

def login_view(request):
    """Login view."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user, backend='accounts.backends.EmailBackend')
                messages.success(request, 'Successfully logged in!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        except Exception as e:
            print(f"Login error: {str(e)}")  # Add this for debugging
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')

def register(request):
    """Initial registration view."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Validate required fields
        if not all([email, password1, password2, first_name, last_name]):
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/register.html')
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'accounts/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/register.html')
        
        # Send verification code
        try:
            create_verification_code(email)
            return render(request, 'accounts/verify_email.html', {
                'email': email,
                'password': password1,  # Pass the password to verification page
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'address': address
            })
        except Exception as e:
            messages.error(request, f'Failed to send verification code: {str(e)}')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')

def verify_email(request):
    """Handle email verification."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        verification_code = request.POST.get('verification_code')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        print(f"Debug - POST data received:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Verification Code: {verification_code}")
        print(f"First Name: {first_name}")
        print(f"Last Name: {last_name}")
        print(f"Phone: {phone}")
        print(f"Address: {address}")
        
        # Validate required fields
        if not all([email, password, verification_code, first_name, last_name]):
            print("Debug - Missing required fields")
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/verify_email.html', {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'address': address,
                'error': 'All fields are required'
            })
        
        try:
            # Get the verification code
            print(f"Debug - Looking for verification code: {verification_code} for email: {email}")
            verification = VerificationCode.objects.get(
                email=email,
                code=verification_code,
                is_used=False
            )
            print(f"Debug - Found verification: {verification}")
            print(f"Debug - Code created at: {verification.created_at}")
            print(f"Debug - Is code valid: {verification.is_valid()}")
            
            # Check if code is still valid (24 hours)
            if verification.is_valid():
                print("Debug - Code is valid, creating user")
                # Create the user with all details
                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    address=address,
                    is_active=True
                )
                print(f"Debug - User created: {user}")
                
                # Mark verification code as used
                verification.is_used = True
                verification.save()
                print("Debug - Verification code marked as used")
                
                # Show success message
                messages.success(request, 'Email verification successful! Please login with your credentials.')
                
                # Redirect to login page
                print("Debug - Redirecting to login page")
                return redirect('accounts:login')
            else:
                print("Debug - Code expired")
                messages.error(request, 'Verification code has expired. Please request a new code.')
                return render(request, 'accounts/verify_email.html', {
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'address': address,
                    'error': 'Verification code has expired'
                })
        except VerificationCode.DoesNotExist:
            print("Debug - Verification code not found")
            messages.error(request, 'Invalid verification code.')
            return render(request, 'accounts/verify_email.html', {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'address': address,
                'error': 'Invalid verification code'
            })
        except Exception as e:
            print(f"Debug - Error: {str(e)}")
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'accounts/verify_email.html', {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'address': address,
                'error': str(e)
            })
    
    # GET request - show verification form
    email = request.GET.get('email')
    password = request.GET.get('password')
    first_name = request.GET.get('first_name')
    last_name = request.GET.get('last_name')
    phone = request.GET.get('phone')
    address = request.GET.get('address')
    
    return render(request, 'accounts/verify_email.html', {
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'address': address
    })

def resend_code(request):
    """Resend verification code."""
    email = request.GET.get('email')
    if not email:
        messages.error(request, 'Email address is required.')
        return redirect('accounts:register')
    
    try:
        create_verification_code(email)
        messages.success(request, 'New verification code sent to your email.')
        return redirect('accounts:verify_email')
    except Exception as e:
        messages.error(request, f'Failed to send verification code: {str(e)}')
        return redirect('accounts:register')

def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home')

def contact(request):
    """Contact form view."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        
        # Send email
        email_message = f"""
        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        
        Message:
        {message}
        """
        
        try:
            send_mail(
                subject=f'Contact Form: {subject}',
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
        except Exception as e:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
        
        return redirect('accounts:home')
    
    return render(request, 'home.html')

@login_required
def profile(request):
    """User profile view."""
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    """Edit user profile view."""
    if request.method == 'POST':
        # Get form data
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', '')
        
        # Save changes
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile_edit.html', {'user': request.user})

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get date range for recent items
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Get user statistics
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    
    # Get shipment statistics
    total_shipments = Shipment.objects.count()
    active_shipments = Shipment.objects.filter(status__in=['pending', 'booked', 'picked_up', 'in_transit', 'out_for_delivery']).count()
    in_transit_shipments = Shipment.objects.filter(status='in_transit').count()
    recent_shipments = Shipment.objects.order_by('-created_at')[:5]
    
    # Get warehouse statistics
    total_warehouses = Warehouse.objects.count()
    active_warehouses = Warehouse.objects.filter(is_active=True).count()
    recent_warehouses = Warehouse.objects.order_by('-created_at')[:5]
    
    # Get message statistics
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'recent_users': recent_users,
        'total_shipments': total_shipments,
        'active_shipments': active_shipments,
        'in_transit_shipments': in_transit_shipments,
        'recent_shipments': recent_shipments,
        'total_warehouses': total_warehouses,
        'active_warehouses': active_warehouses,
        'recent_warehouses': recent_warehouses,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
def user_list(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('accounts:profile')
    
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def user_add(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" was created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/user_form.html', {'form': form})

@login_required
def user_detail(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('accounts:profile')
    
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user_profile': user})

@login_required
def user_edit(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:profile')
    
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" was updated successfully.')
            return redirect('accounts:user_detail', pk=user.pk)
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {'form': form, 'user': user})

@login_required
def user_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:profile')
    
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" was deleted successfully.')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset URL
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )
            
            # Send password reset email
            subject = 'Password Reset - Logistics System'
            message = f'''
            Hello,
            
            You requested a password reset for your Logistics System account.
            
            Please click the following link to reset your password:
            {reset_url}
            
            If you didn't request this, please ignore this email.
            
            This link will expire in 24 hours.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('accounts:login')
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return render(request, 'accounts/forgot_password.html')
    
    return render(request, 'accounts/forgot_password.html')

def reset_password(request, uidb64, token):
    try:
        # Decode the user ID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password2:
                if password1 == password2:
                    user.set_password(password1)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully. Please login with your new password.')
                    return redirect('accounts:login')
                else:
                    messages.error(request, 'Passwords do not match.')
            else:
                messages.error(request, 'Please fill in both password fields.')
        
        return render(request, 'accounts/reset_password.html')
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('accounts:login') 