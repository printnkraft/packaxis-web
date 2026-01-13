from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


# Category types for organization
CATEGORY_TYPES = [
    ('product', 'Product Type'),
    ('industry', 'Industry'),
    ('general', 'General'),
]


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # Subcategory support
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPES,
        default='general'
    )
    
    # Display settings
    icon = models.CharField(max_length=50, blank=True, help_text="Material icon name")
    color = models.CharField(max_length=7, default='#0E5B4D', help_text="Hex color code")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    @property
    def is_subcategory(self):
        return self.parent is not None
    
    @property
    def full_path(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name
    
    @property
    def children(self):
        return self.subcategories.filter(is_active=True).order_by('order')
    
    @property
    def product_count(self):
        """Count products in this category and all subcategories"""
        count = self.products.filter(is_active=True).count()
        for sub in self.subcategories.filter(is_active=True):
            count += sub.products.filter(is_active=True).count()
        return count


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    
    # Multiple categories support
    additional_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='additional_products',
        help_text="Additional categories this product belongs to"
    )
    
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_class = models.CharField(max_length=20, default="taxable")

    weight_kg = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    length_cm = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    width_cm = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    stock_qty = models.PositiveIntegerField(default=0)
    low_stock_alert = models.PositiveIntegerField(default=10)

    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)

    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [GinIndex(fields=["search_vector"]) ]

    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def all_categories(self):
        """Get all categories including primary and additional"""
        cats = [self.category]
        cats.extend(list(self.additional_categories.all()))
        return cats
    
    @property
    def primary_image(self):
        """Get the primary/first image"""
        return self.images.first()
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'pk': self.pk})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    color = models.CharField(max_length=64, blank=True)
    size = models.CharField(max_length=64, blank=True)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_qty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.sku}"


class PricingTier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="pricing_tiers")
    min_qty = models.PositiveIntegerField()
    max_qty = models.PositiveIntegerField()
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["min_qty"]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user_email = models.EmailField()
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class InventoryLog(models.Model):
    """Audit trail for inventory changes"""
    class Reason(models.TextChoices):
        SALE = "SALE", "Sale"
        RESTOCK = "RESTOCK", "Restock"
        RETURN = "RETURN", "Return"
        DAMAGE = "DAMAGE", "Damage"
        ADJUSTMENT = "ADJUSTMENT", "Manual Adjustment"
        CANCELLATION = "CANCELLATION", "Order Cancellation"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_logs")
    quantity_change = models.IntegerField()  # Positive for increase, negative for decrease
    reason = models.CharField(max_length=20, choices=Reason.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        change = f"+{self.quantity_change}" if self.quantity_change > 0 else str(self.quantity_change)
        return f"{self.product.sku}: {change} ({self.reason})"
