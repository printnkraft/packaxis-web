from django.db import models


class NewsletterSubscriber(models.Model):
    """Newsletter subscription management"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # User preferences
    preferences = models.JSONField(default=dict, blank=True)  # e.g., {"frequency": "weekly", "topics": ["products", "promotions"]}
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        status = "Active" if self.is_active else "Unsubscribed"
        return f"{self.email} ({status})"
