from django.db import models

class DailyMetrics(models.Model):
    date = models.DateField(unique=True)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    orders = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage

    def __str__(self):
        return str(self.date)

class ProductAnalytics(models.Model):
    product_id = models.IntegerField()
    total_sold = models.PositiveIntegerField(default=0)
    low_stock_alert = models.BooleanField(default=False)

class CustomMetrics(models.Model):
    date = models.DateField()
    b2b_orders = models.PositiveIntegerField(default=0)
    b2c_orders = models.PositiveIntegerField(default=0)
    aov_b2b = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aov_b2c = models.DecimalField(max_digits=10, decimal_places=2, default=0)
