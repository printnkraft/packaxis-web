from rest_framework import serializers
from .models import Basket, BasketLine

class BasketLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketLine
        fields = ["id", "product", "variant", "quantity", "unit_price"]

class BasketSerializer(serializers.ModelSerializer):
    lines = BasketLineSerializer(many=True, read_only=True)
    class Meta:
        model = Basket
        fields = ["id", "owner", "session_key", "lines", "created_at", "updated_at"]
