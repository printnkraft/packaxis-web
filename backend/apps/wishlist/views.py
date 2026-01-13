from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from apps.products.models import Product
from .models import WishlistItem
from .serializers import WishlistItemSerializer


class WishlistItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related("product")

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=product_id)
        item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        # Default delete by WishlistItem id
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["delete"], url_path="by-product/(?P<product_id>[^/.]+)")
    def delete_by_product(self, request, product_id=None):
        # Optional helper to delete by product id if frontend chooses
        qs = self.get_queryset().filter(product_id=product_id)
        if not qs.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
