from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "company_name", "is_verified", "is_staff")
    search_fields = ("email", "company_name", "tax_id")
    list_filter = ("role", "is_verified", "is_staff")
