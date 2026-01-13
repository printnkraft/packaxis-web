import os
import json
import argparse

def run_with_apiclient():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "packaxis.settings")
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient

    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not user:
        print("No user exists. Create one first.")
        return

    client = APIClient()
    client.force_authenticate(user=user)

    r = client.get('/api/accounts/addresses/', HTTP_HOST='localhost')
    print('LIST status:', r.status_code)
    print('LIST data:', json.dumps(r.json(), indent=2))

    payload = {
        'first_name': 'John',
        'last_name': 'Doe',
        'company': '',
        'address1': '123 Main St',
        'address2': 'Unit 5',
        'city': 'Toronto',
        'province': 'ON',
        'postal_code': 'M5V 3A8',
        'country': 'CA',
        'phone': '416-555-0123',
        'is_default_shipping': True,
        'is_default_billing': False,
    }
    r = client.post('/api/accounts/addresses/', payload, format='json', HTTP_HOST='localhost')
    print('CREATE status:', r.status_code)
    print('CREATE data:', json.dumps(r.json(), indent=2))

    r = client.get('/api/accounts/addresses/', HTTP_HOST='localhost')
    print('LIST status:', r.status_code)
    print('LIST data:', json.dumps(r.json(), indent=2))


def run_with_requests(base_url: str):
    import requests
    # Login or register then login
    s = requests.Session()
    email = 'admin@example.com'
    password = 'adminpass123'
    resp = s.post(f"{base_url}/api/accounts/users/login/", json={"email": email, "password": password})
    if resp.status_code != 200:
        import random, string
        email = "test_" + ''.join(random.choice(string.ascii_lowercase) for _ in range(8)) + "@example.com"
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
    print('Login status:', resp.status_code)
    try:
        print('Login response:', resp.text)
    except Exception:
        pass
    print('Set-Cookie:', resp.headers.get('Set-Cookie'))
    # Handle secure cookies on HTTP dev by manually setting them
    try:
        import re
        cookie_header = resp.headers.get('Set-Cookie') or ''
        sid_match = re.search(r'sessionid=([^;]+)', cookie_header)
        csrf_match = re.search(r'csrftoken=([^;]+)', cookie_header)
        if sid_match:
            s.cookies.set('sessionid', sid_match.group(1), domain='127.0.0.1', path='/')
        if csrf_match:
            s.cookies.set('csrftoken', csrf_match.group(1), domain='127.0.0.1', path='/')
            s.headers['X-CSRFToken'] = csrf_match.group(1)
    except Exception:
        pass
    # Configure Authorization header if token/jwt returned
    try:
        j = resp.json() if hasattr(resp, 'json') else {}
    except Exception:
        j = {}
    token = j.get('access') or j.get('token') or j.get('auth_token') or j.get('key')
    if token:
        if j.get('access'):
            s.headers['Authorization'] = f"Bearer {j['access']}"
        else:
            s.headers['Authorization'] = f"Token {token}"

    r = s.get(f"{base_url}/api/accounts/addresses/")
    print('LIST status:', r.status_code)
    print('LIST data:', json.dumps(r.json(), indent=2))

    payload = {
        'first_name': 'John',
        'last_name': 'Doe',
        'company': '',
        'address1': '123 Main St',
        'address2': 'Unit 5',
        'city': 'Toronto',
        'province': 'ON',
        'postal_code': 'M5V 3A8',
        'country': 'CA',
        'phone': '416-555-0123',
        'is_default_shipping': True,
        'is_default_billing': False,
    }
    r = s.post(f"{base_url}/api/accounts/addresses/", json=payload)
    print('CREATE status:', r.status_code)
    print('CREATE data:', json.dumps(r.json(), indent=2))

    r = s.get(f"{base_url}/api/accounts/addresses/")
    print('LIST status:', r.status_code)
    print('LIST data:', json.dumps(r.json(), indent=2))


def main():
    parser = argparse.ArgumentParser(description='Smoke test addresses API')
    parser.add_argument('--base', dest='base', default=os.environ.get('SMOKE_BASE_URL'))
    args = parser.parse_args()

    if args.base:
        run_with_requests(args.base.rstrip('/'))
    else:
        run_with_apiclient()


if __name__ == '__main__':
    main()
