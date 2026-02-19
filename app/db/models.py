# Import ALL models here so SQLAlchemy registers relationships properly

from app.models.tenant import Tenant
from app.models.product import Product
from app.models.sku import SKU
from app.models.competitor_price import CompetitorPrice
from app.models.demand_signal import DemandSignal
from app.models.price_decision import PriceDecision
from app.models.pricing_rl_state import PricingRLState

# Optional export
__all__ = [
    "Tenant",
    "Product",
    "SKU",
    "CompetitorPrice",
    "DemandSignal",
    "PriceDecision",
    "PricingRLState",
]