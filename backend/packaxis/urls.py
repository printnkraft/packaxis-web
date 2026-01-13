from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static
import sys
from pathlib import Path

# Add frontend directory to Python path
frontend_path = Path(__file__).resolve().parent.parent.parent / 'frontend'
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from views import (
    home_view, 
    product_list_view, 
    product_detail_view,
    product_search_ajax,
    cart_view,
    checkout_view,
    account_dashboard_view,
    orders_view,
    order_detail_view,
    addresses_view,
)

from checkout_api import (
    checkout_calculate_view,
    checkout_provinces_view,
    checkout_shipping_zones_view,
    checkout_taxes_view,
    csrf_token_view,
    create_order_view
)

from apps.promotions.views import validate_coupon

urlpatterns = [
    path("admin/", admin.site.urls),

    # Frontend pages with database content
    path("", home_view, name="home"),
    path("products/", product_list_view, name="product_list"),
    path("products/search/", product_search_ajax, name="product_search_ajax"),
    path("products/<int:pk>/", product_detail_view, name="product_detail"),
    path("cart/", cart_view, name="cart"),
    path("checkout/", checkout_view, name="checkout"),
    path("orders/", orders_view, name="orders"),
    path("orders/<str:order_number>/", order_detail_view, name="order_detail"),
    path("account/", account_dashboard_view, name="account_dashboard"),
    path("account/orders/", RedirectView.as_view(url='/account/#orders', permanent=False), name="account_orders_redirect"),
    path("account/addresses/", addresses_view, name="addresses"),

    # Checkout API endpoints
    path("api/checkout/calculate/", checkout_calculate_view, name="checkout_calculate"),
    path("api/checkout/provinces/", checkout_provinces_view, name="checkout_provinces"),
    path("api/checkout/shipping-zones/", checkout_shipping_zones_view, name="checkout_shipping_zones"),
    path("api/checkout/taxes/", checkout_taxes_view, name="checkout_taxes"),
    path("api/csrf-token/", csrf_token_view, name="csrf_token"),
    path("api/order/create/", create_order_view, name="create_order"),
    path("api/coupons/validate/", validate_coupon, name="validate_coupon"),

    # Other API endpoints
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/cart/", include("apps.cart.urls")),
    path("api/promotions/", include("apps.promotions.urls")),
    path("api/shipping/", include("apps.shipping.urls")),
    path("api/taxes/", include("apps.taxes.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/wishlist/", include("apps.wishlist.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/communications/", include("apps.communications.urls")),
    
    # Content pages (Blog, FAQ)
    path("", include("apps.content.urls")),

    # allauth
    path("accounts/", include("allauth.urls")),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
