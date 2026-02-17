# app/services/pricing_rules.py
from typing import Optional

def enforce_min_margin(price: float, cost_price: float, min_margin: float = 0.1) -> float:
    min_price = cost_price * (1 + min_margin)
    return max(price, min_price)


def enforce_competitor_cap(price: float, competitor_price: Optional[float]) -> float:
    if competitor_price:
        return min(price, competitor_price)
    return price


def apply_all_rules(price: float, cost_price: float, competitor_price: Optional[float]):
    price = enforce_min_margin(price, cost_price)
    price = enforce_competitor_cap(price, competitor_price)
    return round(price, 2)