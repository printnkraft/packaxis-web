import os
from decimal import Decimal

# Placeholder real-time rate integration functions (env-driven)
# In production, these should call respective carrier APIs with credentials


def get_canadapost_rate(weight_kg: float, destination_postal: str) -> Decimal:
    return Decimal("10.00") + Decimal(weight_kg) * Decimal("2.00")


def get_ups_rate(weight_kg: float, destination_postal: str) -> Decimal:
    return Decimal("12.00") + Decimal(weight_kg) * Decimal("2.50")


def get_fedex_rate(weight_kg: float, destination_postal: str) -> Decimal:
    return Decimal("11.00") + Decimal(weight_kg) * Decimal("2.25")
