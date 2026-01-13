from rest_framework import serializers
from .models import ProvinceTaxRate

class ProvinceTaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvinceTaxRate
        fields = "__all__"
