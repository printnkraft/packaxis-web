from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .tasks import send_welcome_email

@receiver(post_save, sender=User)
def handle_user_created(sender, instance: User, created, **kwargs):
    if created and instance.email:
        # Send welcome/verification email asynchronously
        send_welcome_email.delay(instance.id)
        # Optionally set is_verified for social accounts later via allauth signals
