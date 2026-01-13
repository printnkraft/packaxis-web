from django.db import models

class ShippingMethod(models.Model):
    CARRIER_CHOICES = [
        ("Canada Post", "Canada Post"),
        ("UPS", "UPS"),
        ("FedEx", "FedEx"),
    ]
    SERVICE_CHOICES = [
        ("standard", "Standard"),
        ("express", "Express"),
        ("overnight", "Overnight"),
    ]

    carrier = models.CharField(max_length=50, choices=CARRIER_CHOICES)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cutoff_time = models.TimeField(null=True, blank=True)
    processing_days = models.PositiveIntegerField(default=1)  # Kept for backward compatibility
    min_processing_days = models.PositiveIntegerField(default=1, help_text="Minimum delivery days")
    max_processing_days = models.PositiveIntegerField(default=3, help_text="Maximum delivery days")
    is_active = models.BooleanField(default=True)

    def get_delivery_range(self):
        """Return delivery day range as string"""
        if self.min_processing_days == self.max_processing_days:
            return f"{self.min_processing_days} business day{'s' if self.min_processing_days > 1 else ''}"
        return f"{self.min_processing_days}-{self.max_processing_days} business days"

    def __str__(self):
        return f"{self.carrier} - {self.service_type}"
