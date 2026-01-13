"""
Locust load testing script for Packaxis Packaging Canada E-Commerce Platform.
Tests API endpoints under simulated user load.

Run: locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10
"""

from locust import HttpUser, task, between, events
from random import randint, choice
import time
import json


class PackaxisUser(HttpUser):
    """Simulates a typical user browsing and shopping on Packaxis Packaging Canada."""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token = None
        self.user_id = None
        self.product_id = None
        self.cart_id = None
        self.order_id = None
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.register_and_login()
    
    # ==================== Authentication Tasks ====================
    
    def register_and_login(self):
        """Register a new account and login."""
        email = f"user_{randint(100000, 999999)}@example.com"
        password = "testpass123"
        
        # Register
        response = self.client.post(
            "/api/accounts/users/register/",
            json={
                "email": email,
                "password": password,
                "password_confirm": password,
                "first_name": "Test",
                "last_name": "User",
                "role": choice(["B2C", "B2B"])
            },
            name="/api/accounts/users/register/"
        )
        
        if response.status_code == 201:
            self.user_id = response.json().get('id')
        
        # Login
        login_response = self.client.post(
            "/api/accounts/users/login/",
            json={"email": email, "password": password},
            name="/api/accounts/users/login/"
        )
        
        if login_response.status_code == 200:
            self.auth_token = login_response.json().get('id')
    
    @task(2)
    def get_profile(self):
        """Fetch user profile."""
        self.client.get(
            "/api/accounts/users/profile/",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="/api/accounts/users/profile/"
        )
    
    @task(1)
    def change_password(self):
        """Change password."""
        self.client.post(
            "/api/accounts/users/change_password/",
            json={
                "old_password": "testpass123",
                "new_password": "newpass123",
                "new_password_confirm": "newpass123"
            },
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="/api/accounts/users/change_password/"
        )
    
    # ==================== Product Browsing Tasks ====================
    
    @task(10)
    def browse_products(self):
        """Browse product list (most common activity)."""
        page = randint(1, 5)
        self.client.get(
            f"/api/products/products/?page={page}",
            name="/api/products/products/[page]"
        )
    
    @task(8)
    def search_products(self):
        """Search for products."""
        search_terms = ["bag", "paper", "eco", "brown", "white", "large", "small"]
        search = choice(search_terms)
        
        self.client.get(
            f"/api/products/products/?search={search}",
            name="/api/products/products/?search=[term]"
        )
    
    @task(5)
    def filter_by_category(self):
        """Filter products by category."""
        category_id = randint(1, 10)
        self.client.get(
            f"/api/products/products/?category={category_id}",
            name="/api/products/products/?category=[id]"
        )
    
    @task(7)
    def view_product_details(self):
        """View product details."""
        product_id = randint(1, 100)
        response = self.client.get(
            f"/api/products/products/{product_id}/",
            name="/api/products/products/[id]/"
        )
        if response.status_code == 200:
            self.product_id = product_id
    
    @task(3)
    def get_product_reviews(self):
        """Fetch product reviews."""
        if self.product_id:
            self.client.get(
                f"/api/products/products/{self.product_id}/reviews/",
                name="/api/products/products/[id]/reviews/"
            )
    
    # ==================== Cart Management Tasks ====================
    
    @task(5)
    def add_to_cart(self):
        """Add product to cart."""
        if self.product_id:
            response = self.client.post(
                "/api/cart/basket/add_item/",
                json={
                    "product_variant_id": randint(1, 500),
                    "quantity": randint(1, 10)
                },
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/cart/basket/add_item/"
            )
            if response.status_code == 200:
                self.cart_id = response.json().get('id')
    
    @task(4)
    def view_cart(self):
        """View shopping cart."""
        if self.auth_token:
            self.client.get(
                "/api/cart/basket/",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/cart/basket/"
            )
    
    @task(2)
    def apply_discount(self):
        """Apply discount code to cart."""
        if self.cart_id:
            self.client.patch(
                f"/api/cart/basket/{self.cart_id}/",
                json={"coupon_code": "SAVE10"},
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/cart/basket/[id]/"
            )
    
    @task(3)
    def remove_from_cart(self):
        """Remove item from cart."""
        if self.cart_id:
            self.client.delete(
                f"/api/cart/basket/{self.cart_id}/remove_item/",
                json={"basket_line_id": randint(1, 100)},
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/cart/basket/[id]/remove_item/"
            )
    
    # ==================== Checkout & Payment Tasks ====================
    
    @task(2)
    def create_order(self):
        """Create order from cart."""
        if self.auth_token and self.cart_id:
            response = self.client.post(
                "/api/orders/orders/",
                json={
                    "basket_id": self.cart_id,
                    "shipping_method_id": 1,
                    "shipping_address": {
                        "address_line_1": "123 Main St",
                        "city": "Toronto",
                        "province": "ON",
                        "postal_code": "M1A 1A1"
                    }
                },
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/orders/orders/"
            )
            if response.status_code == 201:
                self.order_id = response.json().get('id')
    
    @task(2)
    def create_stripe_intent(self):
        """Create Stripe payment intent."""
        if self.auth_token and self.order_id:
            self.client.post(
                "/api/payments/stripe/intent/",
                json={"order_id": self.order_id},
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/payments/stripe/intent/"
            )
    
    @task(2)
    def create_paypal_payment(self):
        """Create PayPal payment."""
        if self.auth_token and self.order_id:
            self.client.post(
                "/api/payments/paypal/create/",
                json={"order_id": self.order_id},
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/payments/paypal/create/"
            )
    
    # ==================== Order History Tasks ====================
    
    @task(3)
    def view_orders(self):
        """View order history."""
        if self.auth_token:
            self.client.get(
                "/api/orders/orders/",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/orders/orders/"
            )
    
    @task(2)
    def view_order_details(self):
        """View specific order details."""
        if self.auth_token and self.order_id:
            self.client.get(
                f"/api/orders/orders/{self.order_id}/",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                name="/api/orders/orders/[id]/"
            )
    
    # ==================== Shipping & Tax Tasks ====================
    
    @task(2)
    def get_shipping_methods(self):
        """Get available shipping methods."""
        self.client.get(
            "/api/shipping/methods/",
            name="/api/shipping/methods/"
        )
    
    @task(2)
    def calculate_tax(self):
        """Calculate tax for shipping address."""
        self.client.post(
            "/api/shipping/calculate_tax/",
            json={"province": choice(["ON", "QC", "BC", "AB"])},
            name="/api/shipping/calculate_tax/"
        )
    
    # ==================== Admin Dashboard Tasks ====================
    
    @task(1)
    def admin_dashboard(self):
        """Access admin dashboard (if user is staff)."""
        self.client.get(
            "/admin/dashboard/",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="/admin/dashboard/"
        )


class AdminUser(HttpUser):
    """Simulates admin user behavior (less frequent)."""
    
    wait_time = between(5, 15)  # Admins spend more time per action
    
    def on_start(self):
        """Login as admin."""
        # In production, use actual admin credentials
        self.client.post(
            "/api/accounts/users/login/",
            json={"email": "admin@example.com", "password": "adminpass123"}
        )
    
    @task(5)
    def view_dashboard(self):
        """View admin dashboard."""
        self.client.get("/admin/dashboard/")
    
    @task(3)
    def view_all_orders(self):
        """View all orders (not just own)."""
        self.client.get(
            "/api/orders/orders/?page=1",
            headers={"X-Admin": "true"}
        )
    
    @task(2)
    def view_customers(self):
        """View customer list."""
        self.client.get("/api/accounts/users/")
    
    @task(2)
    def export_reports(self):
        """Export various reports."""
        self.client.get("/admin/revenue-export/")
        self.client.get("/admin/orders-export/")
        self.client.get("/admin/customers-export/")
    
    @task(1)
    def check_payments(self):
        """Review payment history."""
        self.client.get("/api/payments/payments/")


# ==================== Event Handlers ====================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("\n" + "="*50)
    print("Packaxis Packaging Canada Load Test Started")
    print("="*50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("\n" + "="*50)
    print("Load Test Summary")
    print("="*50)
    
    for group in environment.stats.entries:
        entry = environment.stats.entries[group]
        print(f"\n{group}")
        print(f"  Requests: {entry.num_requests}")
        print(f"  Failures: {entry.num_failures}")
        print(f"  Avg Response Time: {entry.avg_response_time}ms")
        print(f"  Min Response Time: {entry.min_response_time}ms")
        print(f"  Max Response Time: {entry.max_response_time}ms")
        print(f"  95th Percentile: {entry.get_response_time_percentile(0.95)}ms")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Called for each request."""
    if exception:
        print(f"ERROR: {name} - {exception}")
    elif response_time > 1000:
        print(f"SLOW: {name} - {response_time}ms")


# ==================== Test Configuration ====================

"""
Run tests with different scenarios:

# Light load (10 users)
locust -f locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=5m

# Medium load (100 users)
locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=15m

# Heavy load (1000 users) - recommended for production servers
locust -f locustfile.py --host=http://localhost:8000 --users=1000 --spawn-rate=50 --run-time=30m

# Headless (no web UI)
locust -f locustfile.py --host=http://localhost:8000 --users=500 --spawn-rate=25 --run-time=30m --headless

# Expected Results (healthy system):
- Response time <100ms for 95th percentile
- <1% error rate
- Can handle 1000+ concurrent users
"""
