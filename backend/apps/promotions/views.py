from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
from .models import Discount
from .serializers import DiscountSerializer

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = DiscountSerializer


@api_view(['POST'])
def validate_coupon(request):
    """
    Validate a coupon code and return discount details.
    
    Expected POST body:
    {
        "code": "SAVE10",
        "subtotal": 100.00
    }
    """
    code = request.data.get('code', '').strip().upper()
    subtotal = Decimal(str(request.data.get('subtotal', 0)))
    
    if not code:
        return Response({
            'valid': False,
            'message': 'Please enter a coupon code'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        discount = Discount.objects.get(code__iexact=code, is_active=True)
    except Discount.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'Invalid coupon code'
        }, status=status.HTTP_200_OK)
    
    now = timezone.now()
    
    # Check validity period
    if discount.valid_from > now:
        return Response({
            'valid': False,
            'message': 'This coupon is not yet active'
        }, status=status.HTTP_200_OK)
    
    if discount.valid_to < now:
        return Response({
            'valid': False,
            'message': 'This coupon has expired'
        }, status=status.HTTP_200_OK)
    
    # Check usage limit
    if discount.usage_limit and discount.usage_count >= discount.usage_limit:
        return Response({
            'valid': False,
            'message': 'This coupon has reached its usage limit'
        }, status=status.HTTP_200_OK)
    
    # Check minimum order value
    if subtotal < discount.min_order_value:
        return Response({
            'valid': False,
            'message': f'Minimum order of ${discount.min_order_value:.2f} required for this coupon'
        }, status=status.HTTP_200_OK)
    
    # Determine discount type and value
    if discount.percentage:
        discount_type = 'percentage'
        discount_value = float(discount.percentage)
        calculated_discount = subtotal * (discount.percentage / 100)
        label = f'{discount.percentage}% off'
    elif discount.fixed_amount:
        discount_type = 'fixed'
        discount_value = float(discount.fixed_amount)
        calculated_discount = min(discount.fixed_amount, subtotal)
        label = f'${discount.fixed_amount:.2f} off'
    else:
        return Response({
            'valid': False,
            'message': 'Coupon configuration error'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'valid': True,
        'code': discount.code,
        'discount_type': discount_type,
        'discount_value': discount_value,
        'calculated_discount': float(calculated_discount),
        'label': label,
        'applies_to_shipping': discount.applies_to_shipping,
        'message': f'Coupon applied! You save {label}'
    }, status=status.HTTP_200_OK)
