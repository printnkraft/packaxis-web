import stripe
import paypalrestsdk
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_create_payment_intent(amount_cents: int, currency: str = "cad"):
    return stripe.PaymentIntent.create(amount=amount_cents, currency=currency)


def paypal_create_payment(amount: str, currency: str = "CAD"):
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": amount, "currency": currency}
        }],
        "redirect_urls": {"return_url": "https://example.com/", "cancel_url": "https://example.com/"},
    })
    return payment
