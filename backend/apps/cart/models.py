from django.db import models
from django.conf import settings
from apps.products.models import Product, ProductVariant

class Basket(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="baskets")
    session_key = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def merge_from(self, other: "Basket"):
        for line in other.lines.all():
            self.add(line.product, line.variant, line.quantity)
        other.delete()

    def add(self, product: Product, variant: ProductVariant | None, quantity: int):
        line, _ = BasketLine.objects.get_or_create(
            basket=self,
            product=product,
            variant=variant,
            defaults={"quantity": 0},
        )
        line.quantity += quantity
        line.save()

    def subtotal(self):
        return sum([l.extended_price() for l in self.lines.all()])

class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def extended_price(self):
        return self.quantity * self.unit_price
