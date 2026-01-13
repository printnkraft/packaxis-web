import os
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "packaxis.settings")
import django

django.setup()

from django.utils import timezone
from apps.taxes.models import ProvinceTaxRate
from apps.shipping.models import ShippingMethod
from apps.promotions.models import Discount
from apps.products.models import Category, Product, PricingTier


def seed_taxes():
    data = {
        'ON': {'gst': 0.0, 'pst': 0.0, 'total': 13.0},
        'QC': {'gst': 5.0, 'pst': 9.975, 'total': 14.975},
        'BC': {'gst': 5.0, 'pst': 7.0, 'total': 12.0},
        'AB': {'gst': 5.0, 'pst': 0.0, 'total': 5.0},
        'SK': {'gst': 5.0, 'pst': 6.0, 'total': 11.0},
        'MB': {'gst': 5.0, 'pst': 7.0, 'total': 12.0},
        'NB': {'gst': 0.0, 'pst': 0.0, 'total': 15.0},
        'NL': {'gst': 0.0, 'pst': 0.0, 'total': 15.0},
        'NS': {'gst': 0.0, 'pst': 0.0, 'total': 15.0},
        'PE': {'gst': 0.0, 'pst': 0.0, 'total': 15.0},
        'YT': {'gst': 5.0, 'pst': 0.0, 'total': 5.0},
        'NT': {'gst': 5.0, 'pst': 0.0, 'total': 5.0},
        'NU': {'gst': 5.0, 'pst': 0.0, 'total': 5.0},
    }
    for prov, rates in data.items():
        ProvinceTaxRate.objects.update_or_create(
            province=prov,
            defaults={
                'gst_rate': rates['gst'],
                'pst_rate': rates['pst'],
                'total_rate': rates['total'],
                'is_active': True,
            }
        )
    print('Seeded taxes for provinces')


def seed_shipping():
    shipping_defs = [
        {'carrier': 'Canada Post', 'service_type': 'standard', 'base_rate': 9.99, 'per_kg_rate': 0.50, 'processing_days': 5},
        {'carrier': 'UPS', 'service_type': 'express', 'base_rate': 19.99, 'per_kg_rate': 1.00, 'processing_days': 2},
        {'carrier': 'FedEx', 'service_type': 'overnight', 'base_rate': 39.99, 'per_kg_rate': 2.00, 'processing_days': 1},
    ]
    for s in shipping_defs:
        ShippingMethod.objects.update_or_create(
            carrier=s['carrier'], service_type=s['service_type'],
            defaults={
                'base_rate': s['base_rate'],
                'per_kg_rate': s['per_kg_rate'],
                'processing_days': s['processing_days'],
                'is_active': True,
            }
        )
    print('Seeded shipping methods')


def seed_discounts():
    now = timezone.now()
    Discount.objects.update_or_create(
        code='SAVE10',
        defaults={
            'percentage': 10.0,
            'fixed_amount': None,
            'min_order_value': 0,
            'valid_from': now - datetime.timedelta(days=1),
            'valid_to': now + datetime.timedelta(days=30),
            'usage_limit': None,
            'usage_count': 0,
            'applies_to_shipping': False,
            'is_active': True,
        }
    )
    Discount.objects.update_or_create(
        code='SAVE20',
        defaults={
            'percentage': 20.0,
            'fixed_amount': None,
            'min_order_value': 100.0,
            'valid_from': now - datetime.timedelta(days=1),
            'valid_to': now + datetime.timedelta(days=30),
            'usage_limit': 1000,
            'usage_count': 0,
            'applies_to_shipping': False,
            'is_active': True,
        }
    )
    print('Seeded discounts')


def seed_products():
    cat, _ = Category.objects.update_or_create(slug='bags', defaults={'name': 'Bags', 'description': 'Eco-friendly bags'})
    p, _ = Product.objects.update_or_create(
        sku='PB-001',
        defaults={
            'name': 'Eco Paper Bag',
            'description': 'Durable, recycled paper bag ideal for restaurants.',
            'long_description': 'Made from 100% recycled materials. Sturdy handles. Food-safe.',
            'category': cat,
            'retail_price': 29.99,
            'tax_class': 'taxable',
            'weight_kg': 0.150,
            'length_cm': 28.0,
            'width_cm': 15.0,
            'height_cm': 33.0,
            'stock_qty': 500,
            'low_stock_alert': 25,
            'attributes': {'material': 'recycled_paper', 'color': 'kraft'},
            'is_active': True,
            'seo_title': 'Eco Paper Bag',
            'seo_description': 'Eco-friendly recycled paper bag for restaurants and retail.',
        }
    )
    PricingTier.objects.update_or_create(product=p, min_qty=10, max_qty=49, defaults={'wholesale_price': 27.99})
    PricingTier.objects.update_or_create(product=p, min_qty=50, max_qty=99, defaults={'wholesale_price': 25.99})
    PricingTier.objects.update_or_create(product=p, min_qty=100, max_qty=100000, defaults={'wholesale_price': 23.99})
    print('Seeded products and pricing tiers')


def main():
    seed_taxes()
    seed_shipping()
    seed_discounts()
    seed_products()
    print('Demo data seeding complete.')


if __name__ == '__main__':
    main()
