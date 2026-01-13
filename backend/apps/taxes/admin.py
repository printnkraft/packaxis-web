from django.contrib import admin
from .models import ProvinceTaxRate

@admin.register(ProvinceTaxRate)
class ProvinceTaxRateAdmin(admin.ModelAdmin):
    list_display = ("province", "gst_rate", "pst_rate", "total_rate", "is_active")
    search_fields = ("province",)
    list_filter = ("is_active",)
