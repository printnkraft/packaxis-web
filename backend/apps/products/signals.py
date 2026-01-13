from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product

@receiver(post_save, sender=Product)
def product_updated(sender, instance: Product, **kwargs):
    # Placeholder for search vector update logic if needed via triggers or background tasks
    pass
