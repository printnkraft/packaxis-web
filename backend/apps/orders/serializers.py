from rest_framework import serializers
from .models import Order, OrderLine, OrderNote, ShipmentTracking, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class OrderLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderLine
        fields = ["id", "product", "product_name", "product_image", "variant", "quantity", "unit_price"]
    
    def get_product_image(self, obj):
        if obj.product and obj.product.images.exists():
            return obj.product.images.first().image.url
        return None


class OrderNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderNote
        fields = ["id", "content", "is_internal", "author_name", "created_at"]
    
    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.email
        return "System"


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ShipmentTracking
        fields = [
            "id", "carrier", "tracking_number", "tracking_url", 
            "status", "status_display", "estimated_delivery", 
            "created_at", "last_updated"
        ]


class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    shipments = ShipmentTrackingSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount = serializers.DecimalField(source='total', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer",
            "status",
            "status_display",
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "total",
            "total_amount",
            "shipping_address",
            "billing_address",
            "payment_method",
            "transaction_id",
            "notes_customer",
            "notes_internal",
            "po_number",
            "created_at",
            "shipped_at",
            "delivered_at",
            "lines",
            "shipments",
            "notes",
        ]
    
    def get_notes(self, obj):
        # Only return non-internal notes to customers
        public_notes = obj.notes.filter(is_internal=False)
        return OrderNoteSerializer(public_notes, many=True).data
