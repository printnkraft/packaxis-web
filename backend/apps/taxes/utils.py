from decimal import Decimal
from .models import ProvinceTaxRate


def calculate_tax(subtotal: Decimal, province_code: str) -> dict:
    try:
        rate = ProvinceTaxRate.objects.get(province=province_code, is_active=True)
    except ProvinceTaxRate.DoesNotExist:
        return {"gst": Decimal("0.00"), "pst": Decimal("0.00"), "total": Decimal("0.00")}
    gst = (subtotal * (rate.gst_rate / Decimal("100"))).quantize(Decimal("0.01"))
    pst = (subtotal * (rate.pst_rate / Decimal("100"))).quantize(Decimal("0.01"))
    total = gst + pst
    return {"gst": gst, "pst": pst, "total": total}
