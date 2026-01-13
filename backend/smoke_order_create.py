import os
import json
import random
import string
import argparse

USE_BASE = os.environ.get("SMOKE_BASE_URL")


def rand_email():
    return "test_" + ''.join(random.choice(string.ascii_lowercase) for _ in range(8)) + "@example.com"


def run_with_apiclient():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "packaxis.settings")
    import django
    django.setup()
    from rest_framework.test import APIClient

    client = APIClient()

    # Attempt login; if fails, register then login
    email = "admin@example.com"
    password = "adminpass123"
    resp = client.post('/api/accounts/users/login/', {"email": email, "password": password}, format='json', HTTP_HOST='localhost')
    if resp.status_code != 200:
        email = rand_email()
        password = "StrongPass123!"
        r = client.post('/api/accounts/users/register/', {
            "email": email,
            "password": password,
            "password_confirm": password,
            "first_name": "Test",
            "last_name": "User"
        }, format='json', HTTP_HOST='localhost')
        assert r.status_code in (200, 201), f"Register failed: {r.status_code} {r.content}"
        resp = client.post('/api/accounts/users/login/', {"email": email, "password": password}, format='json', HTTP_HOST='localhost')
        assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.content}"
    print("Logged in as:", json.loads(resp.content).get('email', email))

    # Build items (assumes product id 1 exists)
    items = [
        {"id": 1, "productId": 1, "productName": "Demo Product", "price": 9.99, "quantity": 2}
    ]

    # Calculate totals
    calc = client.post('/api/checkout/calculate/', {
        "postal_code": "M5V 3A8",
        "shipping_method": "standard",
        "items": items
    }, format='json', HTTP_HOST='localhost')
    assert calc.status_code == 200, f"Calc failed: {calc.status_code} {calc.content}"
    data = json.loads(calc.content)
    print("Calculated total:", data.get('total'))

    # Create order
    payload = {
        "items": items,
        "address": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "4165550000",
            "street_address": "123 Main St",
            "street_address_2": "",
            "city": "Toronto",
            "province": data.get('province', 'ON'),
            "postal_code": "M5V 3A8"
        },
        "shipping": {"method": "standard", "cost": data.get('shipping', 9.99)},
        "payment": {"method": "card"},
        "totals": {
            "subtotal": data.get('subtotal'),
            "tax": data.get('tax'),
            "shipping": data.get('shipping'),
            "discount": data.get('discount'),
            "total": data.get('total')
        }
    }
    create = client.post('/api/order/create/', payload, format='json', HTTP_HOST='localhost')
    print("Create status:", create.status_code)
    assert create.status_code == 200, f"Create failed: {create.status_code} {create.content}"
    res = json.loads(create.content)
    print("Order number:", res.get('order_number'))
    print("Redirect URL:", res.get('redirect_url'))


def run_with_requests(base_url: str):
    import requests

    s = requests.Session()
    email = "admin@example.com"
    password = "adminpass123"

    resp = s.post(f"{base_url}/api/accounts/users/login/", json={"email": email, "password": password})
    if resp.status_code != 200:
        email = rand_email()
        password = "StrongPass123!"
        r = s.post(f"{base_url}/api/accounts/users/register/", json={
            "email": email,
            "password": password,
            "password_confirm": password,
            "first_name": "Test",
            "last_name": "User"
        })
        assert r.status_code in (200, 201), f"Register failed: {r.status_code} {r.text}"
        resp = s.post(f"{base_url}/api/accounts/users/login/", json={"email": email, "password": password})
        assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    print("Logged in as:", resp.json().get('email', email))

    items = [
        {"id": 1, "productId": 1, "productName": "Demo Product", "price": 9.99, "quantity": 2}
    ]

    calc = s.post(f"{base_url}/api/checkout/calculate/", json={
        "postal_code": "M5V 3A8",
        "shipping_method": "standard",
        "items": items
    })
    assert calc.status_code == 200, f"Calc failed: {calc.status_code} {calc.text}"
    data = calc.json()
    print("Calculated total:", data.get('total'))

    payload = {
        "items": items,
        "address": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "4165550000",
            "street_address": "123 Main St",
            "street_address_2": "",
            "city": "Toronto",
            "province": data.get('province', 'ON'),
            "postal_code": "M5V 3A8"
        },
        "shipping": {"method": "standard", "cost": data.get('shipping', 9.99)},
        "payment": {"method": "card"},
        "totals": {
            "subtotal": data.get('subtotal'),
            "tax": data.get('tax'),
            "shipping": data.get('shipping'),
            "discount": data.get('discount'),
            "total": data.get('total')
        }
    }
    create = s.post(f"{base_url}/api/order/create/", json=payload)
    print("Create status:", create.status_code)
    assert create.status_code == 200, f"Create failed: {create.status_code} {create.text}"
    res = create.json()
    print("Order number:", res.get('order_number'))
    print("Redirect URL:", res.get('redirect_url'))


def main():
    parser = argparse.ArgumentParser(description="Smoke test for order creation")
    parser.add_argument("--base", dest="base", default=os.environ.get("SMOKE_BASE_URL"), help="Base URL of live server (e.g., http://127.0.0.1:8000)")
    args = parser.parse_args()

    if args.base:
        run_with_requests(args.base.rstrip("/"))
    else:
        run_with_apiclient()


if __name__ == "__main__":
    main()
