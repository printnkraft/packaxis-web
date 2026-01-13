import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(user_id: int):
    user = User.objects.get(id=user_id)
    subject = "Welcome to Packaxis Packaging Canada"
    html_content = render_to_string("emails/welcome.html", {"user": user})
    msg = EmailMultiAlternatives(subject, html_content, to=[user.email])
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send(fail_silently=False)
    except Exception as exc:
        # Do not block user creation if email provider is misconfigured in dev
        logger.warning("Welcome email failed: %s", exc)
