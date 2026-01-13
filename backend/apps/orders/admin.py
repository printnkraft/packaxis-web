from django.contrib import admin
from .models import Order, OrderLine, Address, OrderNote, ShipmentTracking

class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0

class OrderNoteInline(admin.StackedInline):
    model = OrderNote
    extra = 1
    fields = ('author', 'content', 'is_internal', 'created_at')
    readonly_fields = ('created_at',)

class ShipmentTrackingInline(admin.StackedInline):
    model = ShipmentTracking
    extra = 1
    fields = ('carrier', 'tracking_number', 'tracking_url', 'status', 'estimated_delivery', 'last_updated')
    readonly_fields = ('last_updated',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "customer__email")
    inlines = [OrderLineInline, OrderNoteInline, ShipmentTrackingInline]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("address1", "city", "province", "postal_code", "country")
    search_fields = ("address1", "city", "postal_code")

@admin.register(OrderNote)
class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ("order", "author", "is_internal", "created_at")
    list_filter = ("is_internal", "created_at")
    search_fields = ("order__order_number", "content")

@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ("order", "carrier", "tracking_number", "status", "last_updated")
    list_filter = ("carrier", "status", "created_at")
    search_fields = ("order__order_number", "tracking_number")
