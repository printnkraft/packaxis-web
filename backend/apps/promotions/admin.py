from django.contrib import admin
from .models import Discount

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("code", "percentage", "fixed_amount", "valid_from", "valid_to", "is_active")
    search_fields = ("code",)
    list_filter = ("is_active",)
