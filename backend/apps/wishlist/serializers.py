from rest_framework import serializers
from apps.products.models import Product
from .models import WishlistItem


class WishlistProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    price = serializers.DecimalField(source="retail_price", max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = ["id", "name", "price", "image_url", "stock_qty"]

    def get_image_url(self, obj: Product):
        img = obj.images.first()
        if not img:
            return None
        try:
            # Use DRF request to build absolute URL if available
            request = self.context.get("request")
            url = img.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return None


class WishlistItemSerializer(serializers.ModelSerializer):
    product = WishlistProductSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "created_at"]
