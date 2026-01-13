from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant, PricingTier, Review

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "position"]

class PricingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingTier
        fields = ["min_qty", "max_qty", "wholesale_price"]

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "color", "size", "additional_price", "stock_qty"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    pricing_tiers = PricingTierSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "long_description",
            "category",
            "retail_price",
            "tax_class",
            "weight_kg",
            "length_cm",
            "width_cm",
            "height_cm",
            "stock_qty",
            "low_stock_alert",
            "attributes",
            "is_active",
            "seo_title",
            "seo_description",
            "images",
            "variants",
            "pricing_tiers",
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "product", "user_email", "rating", "comment", "verified_purchase", "created_at"]
