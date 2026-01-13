from django.contrib import admin
from .models import ShippingMethod

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("carrier", "service_type", "base_rate", "per_kg_rate", "delivery_range", "is_active")
    list_filter = ("carrier", "service_type", "is_active")
    fieldsets = (
        ('Shipping Information', {
            'fields': ('carrier', 'service_type', 'is_active')
        }),
        ('Pricing', {
            'fields': ('base_rate', 'per_kg_rate')
        }),
        ('Processing Time', {
            'fields': ('min_processing_days', 'max_processing_days', 'processing_days', 'cutoff_time'),
            'description': 'Set min and max processing days for delivery range (e.g., 5-7 days). Processing_days is kept for backward compatibility.'
        }),
    )
    
    def delivery_range(self, obj):
        """Display the delivery day range"""
        return obj.get_delivery_range()
    delivery_range.short_description = 'Delivery Time'
