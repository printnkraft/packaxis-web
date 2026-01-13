from django.db import models

class ProvinceTaxRate(models.Model):
    province = models.CharField(max_length=2, unique=True)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.province} ({self.total_rate}%)"
