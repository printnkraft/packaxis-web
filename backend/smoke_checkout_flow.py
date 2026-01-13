import os
import json
import argparse

def run_with_apiclient():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "packaxis.settings")
    import django
    django.setup()
    from rest_framework.test import APIClient
    from django.test import Client as DjangoClient

    api = APIClient()

    html_client = DjangoClient()
    r = html_client.get('/checkout/', HTTP_HOST='localhost')
    print('GET /checkout/ status:', r.status_code)

    r = api.get('/api/checkout/taxes/', HTTP_HOST='localhost')
    print('GET /api/checkout/taxes/ status:', r.status_code)
    taxes = r.json() if r.status_code == 200 else {}
    print('Taxes keys:', list(taxes.get('provinces', {}).keys())[:5])

    r = api.get('/api/checkout/shipping-zones/', HTTP_HOST='localhost')
    print('GET /api/checkout/shipping-zones/ status:', r.status_code)
    zones = r.json() if r.status_code == 200 else {}
    print('Shipping methods:', [z.get('method') for z in zones.get('shipping_zones', [])])

    payload = {
        'postal_code': 'M5V 3A8',
        'shipping_method': 'standard',
        'items': [
            {'id': 1, 'price': 29.99, 'quantity': 2},
            {'id': 2, 'price': 9.50, 'quantity': 1}
        ]
    }
    r = api.post('/api/checkout/calculate/', data=json.dumps(payload), content_type='application/json', HTTP_HOST='localhost')
    print('POST /api/checkout/calculate/ status:', r.status_code)
    data = r.json() if r.status_code in (200, 400) else {}
    print('Calculate response:', json.dumps(data, indent=2))

    if r.status_code == 200:
        print('Subtotal:', data.get('subtotal'))
        print('Tax:', data.get('tax'), 'Label:', data.get('tax_label'))
        print('Shipping:', data.get('shipping'))
        print('Total:', data.get('total'))
    else:
        print('Errors:', data.get('errors'))


def run_with_requests(base_url: str):
    import requests

    r = requests.get(f"{base_url}/checkout/")
    print('GET /checkout/ status:', r.status_code)

    r = requests.get(f"{base_url}/api/checkout/taxes/")
    print('GET /api/checkout/taxes/ status:', r.status_code)
    taxes = r.json() if r.status_code == 200 else {}
    print('Taxes keys:', list(taxes.get('provinces', {}).keys())[:5])

    r = requests.get(f"{base_url}/api/checkout/shipping-zones/")
    print('GET /api/checkout/shipping-zones/ status:', r.status_code)
    zones = r.json() if r.status_code == 200 else {}
    print('Shipping methods:', [z.get('method') for z in zones.get('shipping_zones', [])])

    payload = {
        'postal_code': 'M5V 3A8',
        'shipping_method': 'standard',
        'items': [
            {'id': 1, 'price': 29.99, 'quantity': 2},
            {'id': 2, 'price': 9.50, 'quantity': 1}
        ]
    }
    r = requests.post(f"{base_url}/api/checkout/calculate/", json=payload)
    print('POST /api/checkout/calculate/ status:', r.status_code)
    data = r.json() if r.status_code in (200, 400) else {}
    print('Calculate response:', json.dumps(data, indent=2))

    if r.status_code == 200:
        print('Subtotal:', data.get('subtotal'))
        print('Tax:', data.get('tax'), 'Label:', data.get('tax_label'))
        print('Shipping:', data.get('shipping'))
        print('Total:', data.get('total'))
    else:
        print('Errors:', data.get('errors'))


def main():
    parser = argparse.ArgumentParser(description='Smoke test checkout flow')
    parser.add_argument('--base', dest='base', default=os.environ.get('SMOKE_BASE_URL'))
    args = parser.parse_args()

    if args.base:
        run_with_requests(args.base.rstrip('/'))
    else:
        run_with_apiclient()


if __name__ == '__main__':
    main()
