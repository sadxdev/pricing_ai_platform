# app/db/base_class.py

from app.db.base import Base

# Import ALL models here so Alembic + SQLAlchemy sees them
from app.models.product import Product
from app.models.sku import SKU
from app.models.competitor_price import CompetitorPrice
from app.models.demand_signal import DemandSignal
from app.models.tenant import Tenant

