from decimal import Decimal


def get_b2b_price_for_qty(product, qty: int) -> Decimal:
    tiers = list(product.pricing_tiers.all())
    for t in tiers:
        if t.min_qty <= qty <= t.max_qty:
            return t.wholesale_price
    return Decimal(product.retail_price)
