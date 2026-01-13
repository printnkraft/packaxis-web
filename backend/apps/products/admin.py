from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, PricingTier, Review, InventoryLog


class SubcategoryInline(admin.TabularInline):
    """Inline to show subcategories within a parent category"""
    model = Category
    fk_name = 'parent'
    extra = 0
    fields = ('name', 'slug', 'category_type', 'icon', 'order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    verbose_name = "Subcategory"
    verbose_name_plural = "Subcategories"
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'category_type', 'product_count_display', 'order', 'is_active', 'color_display')
    list_filter = ('parent', 'category_type', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('parent__name', 'order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Hierarchy', {
            'fields': ('parent', 'category_type'),
            'description': 'Set a parent category to make this a subcategory'
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'order', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SubcategoryInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('parent')
    
    def product_count_display(self, obj):
        count = obj.product_count
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return count
    product_count_display.short_description = 'Products'
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border-radius: 4px; border: 1px solid #ccc;"></span>',
            obj.color
        )
    color_display.short_description = 'Color'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class PricingTierInline(admin.TabularInline):
    model = PricingTier
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'retail_price', 'stock_qty', 'is_active', 'categories_display')
    list_filter = ('category', 'is_active', 'additional_categories')
    search_fields = ('sku', 'name')
    filter_horizontal = ('additional_categories',)
    
    fieldsets = (
        (None, {
            'fields': ('sku', 'name', 'description', 'long_description')
        }),
        ('Categories', {
            'fields': ('category', 'additional_categories'),
            'description': 'Primary category is required. Add additional categories to show product in multiple places.'
        }),
        ('Pricing', {
            'fields': ('retail_price', 'tax_class')
        }),
        ('Dimensions', {
            'fields': ('weight_kg', ('length_cm', 'width_cm', 'height_cm')),
            'classes': ('collapse',)
        }),
        ('Inventory', {
            'fields': ('stock_qty', 'low_stock_alert')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Other', {
            'fields': ('attributes', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, PricingTierInline, ProductVariantInline]
    
    def categories_display(self, obj):
        cats = [obj.category.name]
        additional = list(obj.additional_categories.values_list('name', flat=True))
        if additional:
            cats.extend(additional)
        if len(cats) > 1:
            return format_html('<span title="{}">{} (+{})</span>', 
                ', '.join(cats), 
                obj.category.name, 
                len(additional))
        return obj.category.name
    categories_display.short_description = 'Categories'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user_email', 'rating', 'verified_purchase', 'created_at')
    list_filter = ('rating', 'verified_purchase')
    search_fields = ('product__name', 'user_email')


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_change', 'reason', 'created_by', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('product__sku', 'product__name', 'notes')
    readonly_fields = ('created_at',)
