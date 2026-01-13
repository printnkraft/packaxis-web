import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis.settings')
django.setup()

from django.db import connection
from apps.accounts.models import User

# Temporarily disable the signal
from django.db.models.signals import post_save
from apps.accounts.signals import handle_user_created

post_save.disconnect(handle_user_created, sender=User)

# Create superuser if it doesn't exist
if not User.objects.filter(email='admin@packaxis.ca').exists():
    User.objects.create_superuser(
        email='admin@packaxis.ca',
        password='admin12345',
        is_active=True
    )
    print("Superuser created: admin@packaxis.ca / admin12345")
else:
    print("Superuser already exists")
