from django.contrib import admin
from .models import DailyMetrics, ProductAnalytics, CustomMetrics

admin.site.register(DailyMetrics)
admin.site.register(ProductAnalytics)
admin.site.register(CustomMetrics)
