from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeView, UserViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
