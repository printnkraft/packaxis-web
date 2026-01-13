from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order

@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance: Order, **kwargs):
    if not instance.order_number:
        from datetime import datetime
        base = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        instance.order_number = f"PA-{base}-{instance.customer_id}"