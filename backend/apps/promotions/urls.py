from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiscountViewSet, validate_coupon

router = DefaultRouter()
router.register(r"discounts", DiscountViewSet, basename="discount")

urlpatterns = [
    path("", include(router.urls)),
    path("validate/", validate_coupon, name="validate_coupon"),
]
