"""
WSGI config for team_mgmt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
# from waitress import serve # <-- COMMENTED OUT: Not needed for runserver

# Set the default settings module for the 'django' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_mgmt.settings')

# Get the WSGI application for your project
application = get_wsgi_application()

# The Waitress serving code below is removed. 
# It is only required when launching with a command like `python wsgi.py` 
# or for production deployment (which uses a different method).