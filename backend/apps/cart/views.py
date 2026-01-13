from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Basket, BasketLine
from .serializers import BasketSerializer, BasketLineSerializer
from apps.products.models import Product, ProductVariant

class BasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.save()
            session_key = self.request.session.session_key
        return qs.filter(session_key=session_key)

    def perform_create(self, serializer):
        session_key = self.request.session.session_key or self.request.session.save() or self.request.session.session_key
        serializer.save(owner=self.request.user if self.request.user.is_authenticated else None, session_key=session_key)

    @action(detail=True, methods=["post"])
    def add(self, request, pk=None):
        basket = self.get_object()
        product_id = request.data.get("product_id")
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))
        product = get_object_or_404(Product, id=product_id)
        variant = get_object_or_404(ProductVariant, id=variant_id) if variant_id else None
        # Determine unit price (B2B tiering can be applied later)
        unit_price = product.retail_price
        line, _ = BasketLine.objects.get_or_create(basket=basket, product=product, variant=variant, defaults={"quantity": 0, "unit_price": unit_price})
        line.quantity += quantity
        line.unit_price = unit_price
        line.save()
        return Response(BasketSerializer(basket).data)

    @action(detail=True, methods=["post"])
    def remove(self, request, pk=None):
        basket = self.get_object()
        line_id = request.data.get("line_id")
        line = get_object_or_404(BasketLine, id=line_id, basket=basket)
        line.delete()
        return Response(BasketSerializer(basket).data)
