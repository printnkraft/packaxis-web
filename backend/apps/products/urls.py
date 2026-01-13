from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, ReviewViewSet, 
    autocomplete_search, trending_products,
    check_review_eligibility, submit_review
)

router = DefaultRouter()
router.register(r"items", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
    path("autocomplete/", autocomplete_search, name="autocomplete-search"),
    path("trending/", trending_products, name="trending-products"),
    path("<int:product_id>/review-eligibility/", check_review_eligibility, name="review-eligibility"),
    path("<int:product_id>/reviews/", submit_review, name="submit-review"),
]
