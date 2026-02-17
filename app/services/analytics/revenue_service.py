from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_decision import PriceDecision
from app.models.demand_signal import DemandSignal


class RevenueAnalyticsService:

    @staticmethod
    async def get_revenue_metrics(
        db: AsyncSession,
        sku_id: int,
        tenant_id: int
    ) -> dict:

        # --------------------------------------------
        # 1. Total Purchases (actual demand)
        # --------------------------------------------
        purchase_query = await db.execute(
            select(func.sum(DemandSignal.value))
            .where(DemandSignal.sku_id == sku_id)
            .where(DemandSignal.tenant_id == tenant_id)
            .where(DemandSignal.signal_type == "purchases")
        )
        total_purchases = purchase_query.scalar() or 0

        # --------------------------------------------
        # 2. Total Views
        # --------------------------------------------
        views_query = await db.execute(
            select(func.sum(DemandSignal.value))
            .where(DemandSignal.sku_id == sku_id)
            .where(DemandSignal.tenant_id == tenant_id)
            .where(DemandSignal.signal_type == "views")
        )
        total_views = views_query.scalar() or 0

        # --------------------------------------------
        # 3. Average Selling Price (from decisions)
        # --------------------------------------------
        price_query = await db.execute(
            select(func.avg(PriceDecision.recommended_price))
            .where(PriceDecision.sku_id == sku_id)
            .where(PriceDecision.tenant_id == tenant_id)
        )
        avg_price = float(price_query.scalar() or 0)

        # --------------------------------------------
        # 4. Revenue = price * purchases
        # --------------------------------------------
        total_revenue = float(avg_price * total_purchases)

        # --------------------------------------------
        # 5. Conversion Rate
        # --------------------------------------------
        conversion_rate = (
            (total_purchases / total_views) * 100
            if total_views > 0 else 0
        )

        # --------------------------------------------
        # 6. Revenue per unit
        # --------------------------------------------
        revenue_per_unit = avg_price

        return {
            "sku_id": sku_id,
            "tenant_id": tenant_id,
            "total_purchases": total_purchases,
            "total_views": total_views,
            "conversion_rate_percent": round(conversion_rate, 2),
            "average_selling_price": round(avg_price, 2),
            "total_revenue": round(total_revenue, 2),
            "revenue_per_unit": round(revenue_per_unit, 2)
        }

