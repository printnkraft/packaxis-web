from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import ShippingMethod
from .serializers import ShippingMethodSerializer
from .utils import get_canadapost_rate, get_ups_rate, get_fedex_rate

class ShippingRatesView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        weight = float(request.data.get("weight_kg", 0))
        destination_postal = request.data.get("postal_code", "")
        rates = []
        for method in ShippingMethod.objects.filter(is_active=True):
            if method.carrier == "Canada Post":
                rate = get_canadapost_rate(weight, destination_postal)
            elif method.carrier == "UPS":
                rate = get_ups_rate(weight, destination_postal)
            else:
                rate = get_fedex_rate(weight, destination_postal)
            rates.append({
                "carrier": method.carrier,
                "service_type": method.service_type,
                "rate": str(rate),
                "processing_days": method.processing_days,
            })
        return Response({"rates": rates})
