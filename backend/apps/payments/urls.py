from django.urls import path
from .views import StripeIntentView, PayPalCreateView, stripe_webhook, paypal_webhook

urlpatterns = [
    path("stripe/intent/", StripeIntentView.as_view(), name="stripe_intent"),
    path("paypal/create/", PayPalCreateView.as_view(), name="paypal_create"),
    path("webhooks/stripe/", stripe_webhook, name="stripe_webhook"),
    path("webhooks/paypal/", paypal_webhook, name="paypal_webhook"),
]
