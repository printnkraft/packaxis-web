import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Payment
from apps.orders.models import Order
from .utils import stripe_create_payment_intent, paypal_create_payment

logger = logging.getLogger(__name__)

try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
except (ImportError, AttributeError):
    stripe = None


class StripeIntentView(APIView):
    """Create Stripe payment intent for order checkout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        
        try:
            intent = stripe_create_payment_intent(int(order.total * 100))
            payment = Payment.objects.create(
                order=order,
                method="stripe",
                status="PENDING",
                amount=order.total,
                currency="CAD",
                transaction_id=intent.id
            )
            return Response({
                "client_secret": intent.client_secret,
                "payment_id": payment.id,
                "amount": order.total
            })
        except Exception as e:
            logger.error(f"Stripe intent error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PayPalCreateView(APIView):
    """Create PayPal payment for order checkout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        
        try:
            payment_obj = paypal_create_payment(str(order.total))
            payment = Payment.objects.create(
                order=order,
                method="paypal",
                status="PENDING",
                amount=order.total,
                currency="CAD",
                transaction_id=payment_obj.id
            )
            return Response({
                "payment": payment_obj.to_dict(),
                "payment_id": payment.id
            })
        except Exception as e:
            logger.error(f"PayPal creation error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events for payment processing."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not stripe:
        logger.error("Stripe module not loaded")
        return JsonResponse({'error': 'Stripe not configured'}, status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid Stripe payload: {str(e)}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe signature: {str(e)}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle payment success
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        _handle_stripe_payment_success(intent)
    
    # Handle payment failure
    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        _handle_stripe_payment_failure(intent)
    
    # Handle refunds
    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        _handle_stripe_refund(charge)
    
    return JsonResponse({'status': 'received'})


def _handle_stripe_payment_success(intent):
    """Update payment and order when Stripe payment succeeds."""
    try:
        payment = Payment.objects.get(transaction_id=intent['id'])
        payment.status = 'CAPTURED'
        payment.save()
        
        if payment.order:
            payment.order.status = 'PROCESSING'
            payment.order.payment_method = 'stripe'
            payment.order.save()
        logger.info(f"Stripe payment {intent['id']} captured")
    except Payment.DoesNotExist:
        logger.warning(f"Stripe payment {intent['id']} not found in database")


def _handle_stripe_payment_failure(intent):
    """Update payment when Stripe payment fails."""
    try:
        payment = Payment.objects.get(transaction_id=intent['id'])
        payment.status = 'FAILED'
        payment.error_message = intent.get('last_payment_error', {}).get('message', 'Payment declined')
        payment.save()
        logger.error(f"Stripe payment {intent['id']} failed: {payment.error_message}")
    except Payment.DoesNotExist:
        logger.warning(f"Stripe payment {intent['id']} not found in database")


def _handle_stripe_refund(charge):
    """Handle Stripe refund completion."""
    try:
        payment = Payment.objects.get(transaction_id=charge['payment_intent'])
        payment.status = 'REFUNDED'
        payment.save()
        
        if payment.order:
            payment.order.status = 'CANCELLED'
            payment.order.save()
        logger.info(f"Stripe payment {charge['payment_intent']} refunded")
    except Payment.DoesNotExist:
        logger.warning(f"Stripe payment {charge['payment_intent']} not found in database")


@csrf_exempt
@require_POST
def paypal_webhook(request):
    """Handle PayPal webhook events for payment processing."""
    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid PayPal webhook payload")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    
    event_type = event.get('event_type')
    resource = event.get('resource', {})
    
    # Handle approval creation
    if event_type == 'CHECKOUT.ORDER.APPROVED':
        order_id = resource.get('id')
        logger.info(f"PayPal order approved: {order_id}")
    
    # Handle payment capture completion
    elif event_type == 'CHECKOUT.ORDER.COMPLETED':
        _handle_paypal_order_completion(resource)
    
    return JsonResponse({'status': 'received'})


def _handle_paypal_order_completion(resource):
    """Update payment and order when PayPal order completes."""
    try:
        order_id = resource.get('id')
        payment = Payment.objects.get(transaction_id=order_id)
        payment.status = 'CAPTURED'
        payment.save()
        
        if payment.order:
            payment.order.status = 'PROCESSING'
            payment.order.payment_method = 'paypal'
            payment.order.save()
        logger.info(f"PayPal payment {order_id} completed")
    except Payment.DoesNotExist:
        logger.warning(f"PayPal payment {order_id} not found in database")
