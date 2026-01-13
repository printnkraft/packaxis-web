"""
Populate Checkout Configuration Data
Run this script to populate tax rates, shipping methods, and discount coupons
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'packaxis.settings')
django.setup()

from apps.taxes.models import ProvinceTaxRate
from apps.shipping.models import ShippingMethod
from apps.promotions.models import Discount
from django.utils import timezone

def populate_tax_rates():
    """Populate Canadian provincial tax rates"""
    print("Populating tax rates...")
    
    tax_data = [
        # Province, GST%, PST%, Total%
        ('AB', 5.00, 0.00, 5.00),   # Alberta
        ('BC', 5.00, 0.00, 5.00),   # British Columbia
        ('MB', 5.00, 0.00, 5.00),   # Manitoba
        ('NB', 15.00, 0.00, 15.00), # New Brunswick (HST)
        ('NL', 15.00, 0.00, 15.00), # Newfoundland (HST)
        ('NS', 15.00, 0.00, 15.00), # Nova Scotia (HST)
        ('NT', 5.00, 0.00, 5.00),   # Northwest Territories
        ('NU', 5.00, 0.00, 5.00),   # Nunavut
        ('ON', 13.00, 0.00, 13.00), # Ontario (HST)
        ('PE', 15.00, 0.00, 15.00), # Prince Edward Island (HST)
        ('QC', 5.00, 0.00, 5.00),   # Quebec (GST only, PST managed separately)
        ('SK', 5.00, 0.00, 5.00),   # Saskatchewan
        ('YT', 5.00, 0.00, 5.00),   # Yukon
    ]
    
    for province, gst, pst, total in tax_data:
        tax_rate, created = ProvinceTaxRate.objects.update_or_create(
            province=province,
            defaults={
                'gst_rate': gst,
                'pst_rate': pst,
                'total_rate': total,
                'is_active': True
            }
        )
        status = 'Created' if created else 'Updated'
        print(f"  {status}: {province} - {total}%")
    
    print(f"✓ Tax rates populated ({len(tax_data)} provinces)")


def populate_shipping_methods():
    """Populate shipping methods"""
    print("\nPopulating shipping methods...")
    
    shipping_data = [
        # Carrier, Service Type, Base Rate, Per KG Rate, Processing Days
        ('Canada Post', 'standard', 5.00, 0.50, 5),
        ('Canada Post', 'express', 15.00, 1.00, 2),
        ('Canada Post', 'overnight', 25.00, 2.00, 1),
        ('UPS', 'standard', 8.00, 0.75, 4),
        ('UPS', 'express', 20.00, 1.50, 2),
        ('FedEx', 'overnight', 30.00, 2.50, 1),
    ]
    
    for carrier, service, base_rate, per_kg, days in shipping_data:
        method, created = ShippingMethod.objects.update_or_create(
            carrier=carrier,
            service_type=service,
            defaults={
                'base_rate': base_rate,
                'per_kg_rate': per_kg,
                'processing_days': days,
                'is_active': True
            }
        )
        status = 'Created' if created else 'Updated'
        print(f"  {status}: {carrier} - {service.title()} (${base_rate})")
    
    print(f"✓ Shipping methods populated ({len(shipping_data)} methods)")


def populate_discount_coupons():
    """Populate sample discount coupons"""
    print("\nPopulating discount coupons...")
    
    now = timezone.now()
    one_year_later = now + timedelta(days=365)
    
    coupon_data = [
        # Code, Percentage, Fixed Amount, Min Order Value
        ('SAVE10', 10.00, None, 0),
        ('SAVE20', 20.00, None, 100.00),
        ('BULK25', None, 25.00, 250.00),
        ('WELCOME5', None, 5.00, 0),
        ('FREESHIP', None, 15.00, 75.00),  # Covers standard shipping
        ('SUMMER2024', 15.00, None, 50.00),
    ]
    
    for code, percentage, fixed, min_order in coupon_data:
        coupon, created = Discount.objects.update_or_create(
            code=code,
            defaults={
                'percentage': percentage,
                'fixed_amount': fixed,
                'min_order_value': min_order,
                'valid_from': now,
                'valid_to': one_year_later,
                'usage_limit': None,  # Unlimited usage
                'is_active': True
            }
        )
        status = 'Created' if created else 'Updated'
        discount_type = f"{percentage}%" if percentage else f"${fixed}"
        min_text = f" (min ${min_order})" if min_order > 0 else ""
        print(f"  {status}: {code} - {discount_type}{min_text}")
    
    print(f"✓ Discount coupons populated ({len(coupon_data)} coupons)")


def main():
    print("="*60)
    print("POPULATING CHECKOUT CONFIGURATION DATA")
    print("="*60)
    
    try:
        populate_tax_rates()
        populate_shipping_methods()
        populate_discount_coupons()
        
        print("\n" + "="*60)
        print("✓ ALL CONFIGURATION DATA POPULATED SUCCESSFULLY")
        print("="*60)
        print("\nYou can now test the checkout system at:")
        print("  http://localhost:8000/checkout/")
        print("\nTest coupons:")
        print("  SAVE10   - 10% off any order")
        print("  SAVE20   - 20% off orders $100+")
        print("  BULK25   - $25 off orders $250+")
        print("  WELCOME5 - $5 off any order")
        print("  FREESHIP - $15 off (free standard shipping on $75+)")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
