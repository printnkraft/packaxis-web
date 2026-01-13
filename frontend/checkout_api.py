"""
Checkout API views for real-time calculations
Packaxis Checkout System - Backend API (Database-Driven)
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.middleware.csrf import get_token
from django.utils import timezone
from apps.taxes.models import ProvinceTaxRate
from apps.shipping.models import ShippingMethod
from apps.promotions.models import Discount
import logging
from apps.orders.models import Order, OrderLine, Address as OrderAddress
from apps.products.models import Product, ProductVariant

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS (Not configuration - only mappings)
# ============================================================================

POSTAL_CODE_PROVINCES = {
    'A': 'NL', 'B': 'NS', 'C': 'PE', 'E': 'NB',
    'G': 'QC', 'H': 'QC', 'J': 'QC',
    'K': 'ON', 'L': 'ON', 'M': 'ON', 'N': 'ON', 'P': 'ON',
    'R': 'MB', 'S': 'SK', 'T': 'AB', 'V': 'BC',
    'X': 'NT', 'Y': 'YT', 'Z': 'NU'
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_postal_code(postal_code):
    """
    Validate Canadian postal code format (A1A 1A1)
    Returns (is_valid, province, error_message)
    """
    if not postal_code:
        return False, None, 'Postal code is required'
    
    # Remove spaces and convert to uppercase
    postal_code = postal_code.replace(' ', '').upper()
    
    # Check format
    import re
    if not re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', postal_code):
        return False, None, 'Invalid postal code format. Use: A1A 1A1'
    
    # Extract province from first letter
    first_letter = postal_code[0]
    province = POSTAL_CODE_PROVINCES.get(first_letter)
    
    if not province:
        return False, None, 'Unable to identify province from postal code'
    
    return True, province, None


def get_tax_rate(province):
    """Get tax rate for province from database"""
    try:
        tax_rate = ProvinceTaxRate.objects.get(province=province, is_active=True)
        # Determine label based on tax structure
        if tax_rate.pst_rate > 0:
            label = f'GST ({tax_rate.gst_rate}%) + PST ({tax_rate.pst_rate}%)'
        elif tax_rate.total_rate >= 13:
            label = 'HST'
        else:
            label = 'GST'
        
        return {
            'rate': float(tax_rate.total_rate) / 100,  # Convert from percentage to decimal
            'label': label,
            'province': province
        }
    except ProvinceTaxRate.DoesNotExist:
        logger.warning(f'Tax rate not found for province: {province}')
        return {'rate': 0.13, 'label': 'HST', 'province': province}  # Default Ontario rate


def calculate_tax(subtotal, province):
    """Calculate tax based on province from database"""
    tax_info = get_tax_rate(province)
    tax_amount = float(subtotal) * tax_info['rate']
    return round(tax_amount, 2), tax_info


def calculate_shipping_cost(postal_code, shipping_method, weight=0):
    """
    Calculate shipping cost from database based on method and weight
    shipping_method: service_type from ShippingMethod model (e.g., 'standard', 'express', 'overnight')
    """
    try:
        # Get first shipping method from database (in case multiple exist with same service_type)
        method = ShippingMethod.objects.filter(service_type=shipping_method, is_active=True).first()
        
        if not method:
            logger.warning(f'Shipping method not found: {shipping_method}')
            return 5.00  # Default fallback
        
        # Calculate cost: base_rate + (weight * per_kg_rate)
        base_cost = float(method.base_rate)
        weight_cost = float(method.per_kg_rate) * weight if weight > 0 else 0
        total_cost = base_cost + weight_cost
        
        return round(total_cost, 2)
    except Exception as e:
        logger.error(f'Shipping cost calculation error: {str(e)}')
        return 5.00  # Default fallback


def calculate_discount(subtotal, coupon_code):
    """
    Calculate discount from database coupon
    Returns (discount_amount, coupon_info, error_message)
    """
    if not coupon_code:
        return 0.00, None, None
    
    coupon_code = coupon_code.upper().strip()
    
    try:
        # Get coupon from database
        coupon = Discount.objects.get(code=coupon_code, is_active=True)
        
        # Check validity dates
        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_to):
            return 0.00, None, 'This coupon has expired or is not yet valid'
        
        # Check usage limit
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            return 0.00, None, 'This coupon has reached its usage limit'
        
        # Check minimum order value
        if float(subtotal) < float(coupon.min_order_value):
            return 0.00, None, f'Minimum order value of ${coupon.min_order_value} required'
        
        # Calculate discount
        if coupon.percentage:
            discount_amount = float(subtotal) * (float(coupon.percentage) / 100)
            discount_type = 'percentage'
            discount_value = float(coupon.percentage)
        elif coupon.fixed_amount:
            discount_amount = float(coupon.fixed_amount)
            discount_type = 'fixed'
            discount_value = float(coupon.fixed_amount)
        else:
            return 0.00, None, 'Invalid coupon configuration'
        
        coupon_info = {
            'code': coupon.code,
            'type': discount_type,
            'discount': discount_value,
            'label': f'{coupon.code} - {discount_type.title()}'
        }
        
        return round(discount_amount, 2), coupon_info, None
        
    except Discount.DoesNotExist:
        return 0.00, None, f'Invalid coupon code: {coupon_code}'


def calculate_delivery_date(shipping_method, postal_code=None):
    """
    Calculate estimated delivery date from database
    """
    try:
        method = ShippingMethod.objects.filter(service_type=shipping_method, is_active=True).first()
        days = method.processing_days if method else 5  # Default fallback
    except Exception as e:
        logger.error(f'Delivery date calculation error: {str(e)}')
        days = 5  # Default fallback
    
    # Start from tomorrow (business days only)
    delivery_date = datetime.now() + timedelta(days=1)
    
    # Skip weekends
    days_added = 0
    while days_added < days:
        delivery_date += timedelta(days=1)
        if delivery_date.weekday() < 5:  # Monday = 0, Friday = 4
            days_added += 1
    
    return delivery_date.strftime('%a, %b %d, %Y')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(['POST'])
def checkout_calculate_view(request):
    """
    API endpoint for real-time checkout calculations
    POST /api/checkout/calculate/
    
    Request payload:
    {
        "postal_code": "M5V 3A8",
        "province": "ON",  (optional - will be calculated from postal code)
        "shipping_method": "economy",
        "items": [{"id": 1, "price": 10.00, "quantity": 2}, ...],
        "coupon_code": "SAVE10" (optional)
    }
    
    Response:
    {
        "success": true,
        "subtotal": 20.00,
        "tax": 2.60,
        "tax_rate": 0.13,
        "tax_label": "HST",
        "shipping": 5.00,
        "discount": 2.00,
        "total": 25.60,
        "estimated_delivery": "Wed, Feb 12, 2024",
        "coupon": {"label": "Save 10%"},
        "errors": []
    }
    """
    try:
        # Parse request
        data = json.loads(request.body)
        errors = []
        
        logger.info(f'Checkout calculate request: {data}')
        
        # Validate postal code
        postal_code = data.get('postal_code', '').strip()
        is_valid, province, error = validate_postal_code(postal_code)
        
        if not is_valid:
            errors.append(error)
            return JsonResponse({
                'success': False,
                'errors': [error]
            }, status=400)
        
        # Override with province from request if provided
        if data.get('province'):
            province = data['province'].upper()
        
        # Calculate subtotal from items
        items = data.get('items', [])
        subtotal = 0
        total_weight = 0
        
        for item in items:
            price = float(item.get('price', 0))
            quantity = int(item.get('quantity', 1))
            weight = float(item.get('weight', 0))  # Optional
            
            subtotal += price * quantity
            total_weight += weight * quantity
        
        subtotal = round(subtotal, 2)
        
        # Get shipping method - use first match if multiple exist
        shipping_method = data.get('shipping_method', 'standard').lower()
        if not ShippingMethod.objects.filter(service_type=shipping_method, is_active=True).exists():
            # Try to get first active shipping method as fallback
            first_method = ShippingMethod.objects.filter(is_active=True).first()
            shipping_method = first_method.service_type if first_method else 'standard'
        
        # Calculate discount (before tax)
        discount, coupon, coupon_error = calculate_discount(
            subtotal, data.get('coupon_code')
        )
        
        if coupon_error:
            errors.append(coupon_error)
        
        # Apply discount to subtotal
        taxable_amount = subtotal - discount
        
        # Calculate tax
        tax, tax_info = calculate_tax(taxable_amount, province)
        
        # Calculate shipping
        shipping = calculate_shipping_cost(postal_code, shipping_method, total_weight)
        
        # Calculate total
        total = taxable_amount + tax + shipping
        total = round(total, 2)
        
        # Calculate delivery date
        delivery_date = calculate_delivery_date(shipping_method, postal_code)
        
        # Build response
        response = {
            'success': True,
            'subtotal': subtotal,
            'tax': tax,
            'tax_rate': tax_info['rate'],
            'tax_label': tax_info['label'],
            'shipping': shipping,
            'discount': discount,
            'total': total,
            'estimated_delivery': delivery_date,
            'province': province,
            'errors': errors
        }
        
        # Add coupon info if applied
        if coupon:
            response['coupon'] = {
                'code': data.get('coupon_code'),
                'label': coupon['label'],
                'type': coupon['type']
            }
        
        return JsonResponse(response)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'errors': ['Invalid JSON in request body']
        }, status=400)
    
    except Exception as e:
        logger.error(f'Checkout calculation error: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'errors': [f'An error occurred: {str(e)}']
        }, status=500)


@require_http_methods(['GET'])
def checkout_provinces_view(request):
    """
    GET /api/checkout/provinces/
    Returns list of Canadian provinces for dropdown
    """
    provinces = [
        {'code': 'AB', 'name': 'Alberta'},
        {'code': 'BC', 'name': 'British Columbia'},
        {'code': 'MB', 'name': 'Manitoba'},
        {'code': 'NB', 'name': 'New Brunswick'},
        {'code': 'NL', 'name': 'Newfoundland and Labrador'},
        {'code': 'NS', 'name': 'Nova Scotia'},
        {'code': 'NT', 'name': 'Northwest Territories'},
        {'code': 'NU', 'name': 'Nunavut'},
        {'code': 'ON', 'name': 'Ontario'},
        {'code': 'PE', 'name': 'Prince Edward Island'},
        {'code': 'QC', 'name': 'Quebec'},
        {'code': 'SK', 'name': 'Saskatchewan'},
        {'code': 'YT', 'name': 'Yukon'},
    ]
    
    return JsonResponse({
        'success': True,
        'provinces': provinces
    })


@require_http_methods(['GET'])
def checkout_shipping_zones_view(request):
    """
    GET /api/checkout/shipping-zones/
    Returns available shipping methods from database
    """
    try:
        shipping_methods = ShippingMethod.objects.filter(is_active=True).order_by('base_rate')
        zones = []
        
        for method in shipping_methods:
            zones.append({
                'method': method.service_type,
                'label': method.get_service_type_display(),
                'carrier': method.carrier,
                'days': method.get_delivery_range() if hasattr(method, 'get_delivery_range') else f'{method.processing_days} business days',
                'min_days': method.min_processing_days if hasattr(method, 'min_processing_days') else method.processing_days,
                'max_days': method.max_processing_days if hasattr(method, 'max_processing_days') else method.processing_days,
                'base_cost': float(method.base_rate),
                'per_kg_cost': float(method.per_kg_rate),
                'description': method.get_delivery_range() if hasattr(method, 'get_delivery_range') else f'{method.processing_days} business days'
            })
        
        return JsonResponse({
            'success': True,
            'shipping_zones': zones
        })
    except Exception as e:
        logger.error(f'Error fetching shipping zones: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch shipping zones'
        }, status=500)


@require_http_methods(['GET'])
def checkout_taxes_view(request):
    """
    GET /api/checkout/taxes/
    Returns tax rates for all provinces from database
    """
    try:
        tax_rates = ProvinceTaxRate.objects.filter(is_active=True).order_by('province')
        provinces = {}
        
        for tax_rate in tax_rates:
            # Determine label
            if tax_rate.pst_rate > 0:
                label = f'GST + PST'
            elif tax_rate.total_rate >= 13:
                label = 'HST'
            else:
                label = 'GST'
            
            provinces[tax_rate.province] = {
                'rate': float(tax_rate.total_rate) / 100,  # Decimal
                'percentage': f"{tax_rate.total_rate}%",
                'label': label,
                'gst': float(tax_rate.gst_rate),
                'pst': float(tax_rate.pst_rate)
            }
        
        return JsonResponse({
            'success': True,
            'provinces': provinces
        })
    except Exception as e:
        logger.error(f'Error fetching tax rates: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch tax rates'
        }, status=500)


@require_http_methods(['GET'])
def csrf_token_view(request):
    """
    GET /api/csrf-token/
    Returns CSRF token for AJAX requests
    """
    token = get_token(request)
    return JsonResponse({
        'csrfToken': token
    })


# ============================================================================
# ORDER CREATION (Future Enhancement)
# ============================================================================

@csrf_exempt
@require_http_methods(['POST'])
def create_order_view(request):
    """
    POST /api/order/create/
    Creates an order from checkout data
    
    Persists an Order, OrderLines, and address snapshots. Returns redirect URL.
    Supports both authenticated and guest checkouts.
    """
    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ['items', 'address', 'shipping', 'totals']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'errors': [f'Missing required field: {field}']
                }, status=400)
        
        items = data.get('items') or []
        if not items:
            return JsonResponse({
                'success': False,
                'errors': ['No items in order']
            }, status=400)

        addr_payload = data.get('address') or {}
        shipping_payload = data.get('shipping') or {}
        totals = data.get('totals') or {}
        coupon = data.get('coupon') or None

        # Basic address validation (guests must supply email)
        required_address_fields = ['first_name', 'last_name', 'street_address', 'city', 'province', 'postal_code']
        missing_fields = [f for f in required_address_fields if not addr_payload.get(f)]
        guest_email = (data.get('guest_email') or addr_payload.get('email') or '').strip()

        if missing_fields:
            return JsonResponse({
                'success': False,
                'errors': [f"Missing required address field(s): {', '.join(missing_fields)}"]
            }, status=400)

        if not request.user.is_authenticated and not guest_email:
            return JsonResponse({
                'success': False,
                'errors': ['Email is required for guest checkout']
            }, status=400)

        customer = request.user if request.user.is_authenticated else None

        # Create snapshot addresses
        with transaction.atomic():
            shipping_address = OrderAddress.objects.create(
                first_name=addr_payload.get('first_name', ''),
                last_name=addr_payload.get('last_name', ''),
                company='',
                address1=addr_payload.get('street_address', ''),
                address2=addr_payload.get('street_address_2', ''),
                city=addr_payload.get('city', ''),
                province=addr_payload.get('province', ''),
                postal_code=addr_payload.get('postal_code', ''),
                country='CA',
                phone=addr_payload.get('phone', ''),
            )
            # Use same as billing for now
            billing_address = OrderAddress.objects.create(
                first_name=addr_payload.get('first_name', ''),
                last_name=addr_payload.get('last_name', ''),
                company='',
                address1=addr_payload.get('street_address', ''),
                address2=addr_payload.get('street_address_2', ''),
                city=addr_payload.get('city', ''),
                province=addr_payload.get('province', ''),
                postal_code=addr_payload.get('postal_code', ''),
                country='CA',
                phone=addr_payload.get('phone', ''),
            )

            # Generate order number
            base_number = f"PKX{timezone.now().strftime('%Y%m%d%H%M%S')}"
            order_number = base_number
            suffix = 1
            while Order.objects.filter(order_number=order_number).exists():
                order_number = f"{base_number}-{suffix}"
                suffix += 1

            # Create order
            order = Order.objects.create(
                order_number=order_number,
                customer=customer,
                status=Order.Status.PENDING,
                subtotal=Decimal(str(totals.get('subtotal', 0))) if totals else Decimal('0'),
                tax_amount=Decimal(str(totals.get('tax', 0))) if totals else Decimal('0'),
                shipping_cost=Decimal(str(totals.get('shipping', 0))) if totals else Decimal('0'),
                total=Decimal(str(totals.get('total', 0))) if totals else Decimal('0'),
                shipping_address=shipping_address,
                billing_address=billing_address,
                payment_method=(data.get('payment') or {}).get('method', ''),
                guest_email=guest_email or getattr(customer, 'email', ''),
            )

            # Create order lines
            for it in items:
                product_id = it.get('productId') or it.get('id')
                quantity = int(it.get('quantity', 1))
                unit_price = Decimal(str(it.get('price', 0)))
                if not product_id:
                    continue
                try:
                    product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    logger.warning(f"Product not found for order line: {product_id}")
                    continue
                OrderLine.objects.create(
                    order=order,
                    product=product,
                    variant=None,
                    quantity=quantity,
                    unit_price=unit_price,
                )

            # If coupon applied, increment usage count
            if coupon and coupon.get('code'):
                try:
                    disc = Discount.objects.get(code=str(coupon.get('code')).upper())
                    disc.usage_count = (disc.usage_count or 0) + 1
                    disc.save(update_fields=['usage_count'])
                except Discount.DoesNotExist:
                    pass

        redirect_url = f"/orders/{order.order_number}/"

        # Send order confirmation email
        try:
            from apps.communications.tasks import send_order_confirmation
            email = order.guest_email if order.guest_email else (order.customer.email if order.customer else None)
            if email:
                send_order_confirmation.delay(order.id, email)
        except Exception as email_error:
            logger.error(f'Failed to send order confirmation email: {str(email_error)}')
            # Don't fail the order creation if email fails
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'redirect_url': redirect_url,
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'errors': ['Invalid JSON in request body']
        }, status=400)
    
    except Exception as e:
        logger.error(f'Order creation error: {str(e)}')
        return JsonResponse({
            'success': False,
            'errors': ['An error occurred while creating the order']
        }, status=500)

