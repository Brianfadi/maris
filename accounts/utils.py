import random
import string
from django.core.mail import send_mail
from django.conf import settings
from .models import VerificationCode

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    """Send verification code to user's email"""
    subject = 'Email Verification - Maris Logistics'
    message = f'''
    Thank you for registering with Maris Logistics!
    
    Your verification code is: {code}
    
    This code will expire in 24 hours.
    
    If you didn't request this verification, please ignore this email.
    '''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def create_verification_code(email):
    """Create and save a new verification code"""
    print(f"Debug - Creating verification code for email: {email}")
    
    # Invalidate any existing codes for this email
    existing_codes = VerificationCode.objects.filter(email=email, is_used=False)
    print(f"Debug - Found {existing_codes.count()} existing codes")
    
    for code in existing_codes:
        code.is_used = True
        code.save()
    
    # Generate and save new code
    code = generate_verification_code()
    print(f"Debug - Generated new code: {code}")
    
    verification_code = VerificationCode.objects.create(
        email=email,
        code=code
    )
    print(f"Debug - Created verification code object: {verification_code}")
    
    # Send verification email
    try:
        send_verification_email(email, code)
        print(f"Debug - Verification email sent to {email}")
    except Exception as e:
        print(f"Debug - Error sending email: {str(e)}")
        raise
    
    return verification_code 