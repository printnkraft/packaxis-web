import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis.settings')
django.setup()

from django.apps import apps
from django.db import models

# Check all installed apps and their models
for app_config in apps.get_app_configs():
    app_models = list(app_config.get_models())
    if app_models:
        print(f"\n{app_config.name}:")
        for model in app_models:
            fields = [f.name for f in model._meta.get_fields()]
            print(f"  - {model.__name__}: {', '.join(fields[:3])}...")
