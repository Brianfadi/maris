import os
import sys

# Add the application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'logistics.settings'

# Set cPanel environment variable
os.environ['cpanel'] = 'True'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 