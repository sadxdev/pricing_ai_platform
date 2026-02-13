from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.competitor_price import CompetitorPrice
from app.models.demand_signal import DemandSignal


class FeatureService:

    @staticmethod
    async def get_features(db: AsyncSession, sku_id: int) -> dict:

        # --- Competitor Price Aggregation ---
        comp_query = await db.execute(
            select(
                func.avg(CompetitorPrice.competitor_price),
                func.min(CompetitorPrice.competitor_price),
                func.max(CompetitorPrice.competitor_price),
            ).where(CompetitorPrice.sku_id == sku_id)
        )

        row = comp_query.first()

        if row:
            avg_price, min_price, max_price = row
        else:
            avg_price = min_price = max_price = 0

        avg_price = float(avg_price or 0)
        min_price = float(min_price or 0)
        max_price = float(max_price or 0)

        # --- Demand Signals Aggregation ---
        demand_query = await db.execute(
            select(
                DemandSignal.signal_type,
                func.sum(DemandSignal.value)
            )
            .where(DemandSignal.sku_id == sku_id)
            .group_by(DemandSignal.signal_type)
        )

        demand_rows = demand_query.all()

        demand_data = {row[0]: row[1] for row in demand_rows}

        return {
            "avg_competitor_price": avg_price,
            "min_competitor_price": min_price,
            "max_competitor_price": max_price,
            "views": demand_data.get("views", 0),
            "add_to_cart": demand_data.get("add_to_cart", 0),
            "purchases": demand_data.get("purchases", 0),
        }