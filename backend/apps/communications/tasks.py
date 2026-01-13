from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_order_confirmation(order_id: int, to_email: str):
    """Send order confirmation email"""
    from apps.orders.models import Order
    
    order = Order.objects.select_related('customer').prefetch_related('lines__product').get(pk=order_id)
    subject = f"Your Packaxis Order #{order.order_number} Confirmation"
    html_content = render_to_string("emails/order_confirmation.html", {"order": order})
    
    msg = EmailMultiAlternatives(subject, html_content, to=[to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_shipment_notification(order_id: int, tracking_number: str, carrier: str, tracking_url: str = "", estimated_delivery=None):
    """Send shipment notification email with tracking information"""
    from apps.orders.models import Order
    
    order = Order.objects.select_related('customer').prefetch_related('lines__product').get(pk=order_id)
    subject = f"Your Packaxis Order #{order.order_number} Has Shipped!"
    
    context = {
        'order': order,
        'tracking_number': tracking_number,
        'carrier': carrier,
        'tracking_url': tracking_url,
        'estimated_delivery': estimated_delivery,
    }
    
    html_content = render_to_string("emails/shipment_notification.html", context)
    
    msg = EmailMultiAlternatives(subject, html_content, to=[order.customer.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_abandoned_cart_reminder(basket_id: int, discount_code: str = None, discount_amount: str = None):
    """Send abandoned cart reminder email"""
    from apps.cart.models import Basket
    from django.conf import settings
    
    try:
        basket = Basket.objects.select_related('owner').prefetch_related('lines__product').get(pk=basket_id)
        
        # Don't send if cart is empty or already converted to order
        if not basket.lines.exists():
            return
        
        customer_name = basket.owner.first_name if basket.owner and basket.owner.first_name else None
        email = basket.owner.email if basket.owner else None
        
        if not email:
            return
        
        # Calculate cart total
        cart_total = sum(line.product.retail_price * line.quantity for line in basket.lines.all())
        
        # Calculate expiration hours
        if basket.expires_at:
            expiration_hours = int((basket.expires_at - timezone.now()).total_seconds() / 3600)
        else:
            expiration_hours = 24
        
        subject = "Your Cart is Waiting at Packaxis! 🛒"
        
        context = {
            'customer_name': customer_name,
            'cart_items': basket.lines.all(),
            'cart_total': f"{cart_total:.2f}",
            'cart_url': f"{settings.SITE_URL}/cart/",
            'discount_code': discount_code,
            'discount_amount': discount_amount,
            'expiration_hours': expiration_hours,
            'unsubscribe_url': f"{settings.SITE_URL}/unsubscribe/",
        }
        
        html_content = render_to_string("emails/abandoned_cart.html", context)
        
        msg = EmailMultiAlternatives(subject, html_content, to=[email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    
    except Basket.DoesNotExist:
        pass


@shared_task
def send_review_request(order_id: int):
    """Send review request email after order delivery"""
    from apps.orders.models import Order
    from django.conf import settings
    
    try:
        order = Order.objects.select_related('customer').prefetch_related('lines__product').get(pk=order_id)
        
        # Only send if order is delivered
        if order.status != Order.Status.DELIVERED:
            return
        
        subject = "How Was Your Packaxis Experience? ⭐"
        
        context = {
            'order': order,
            'review_url': f"{settings.SITE_URL}/account/orders/{order.order_number}/review/",
        }
        
        html_content = render_to_string("emails/review_request.html", context)
        
        msg = EmailMultiAlternatives(subject, html_content, to=[order.customer.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    
    except Order.DoesNotExist:
        pass


@shared_task
def send_newsletter(subscriber_ids: list, subject: str, html_content: str):
    """Send newsletter to list of subscribers"""
    from apps.communications.models import NewsletterSubscriber
    
    subscribers = NewsletterSubscriber.objects.filter(id__in=subscriber_ids, is_active=True)
    
    for subscriber in subscribers:
        msg = EmailMultiAlternatives(subject, html_content, to=[subscriber.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
