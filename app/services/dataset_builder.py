from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.sku import SKU
from app.models.competitor_price import CompetitorPrice
from app.models.demand_signal import DemandSignal


class DatasetBuilder:

    @staticmethod
    async def build_training_dataset(
        db: AsyncSession,
        tenant_id: int
    ):
        """
        Build ML training dataset per tenant

        Each row represents a SKU with:
        - competitor price stats
        - demand signals
        - target demand (purchases)
        """

        # -----------------------------------------
        # 1. Fetch all SKUs for tenant
        # -----------------------------------------
        sku_result = await db.execute(
            select(SKU.id)
            .where(SKU.tenant_id == tenant_id)
        )

        sku_ids = [row[0] for row in sku_result.all()]

        dataset = []

        # -----------------------------------------
        # 2. Build features per SKU
        # -----------------------------------------
        for sku_id in sku_ids:

            # ---------- Competitor Price Stats ----------
            comp_result = await db.execute(
                select(
                    func.avg(CompetitorPrice.competitor_price),
                    func.min(CompetitorPrice.competitor_price),
                    func.max(CompetitorPrice.competitor_price),
                )
                .where(CompetitorPrice.sku_id == sku_id)
                .where(CompetitorPrice.tenant_id == tenant_id)
            )

            comp_row = comp_result.first()

            avg_price = float(comp_row[0] or 0)
            min_price = float(comp_row[1] or 0)
            max_price = float(comp_row[2] or 0)

            # ---------- Demand Signals ----------
            demand_result = await db.execute(
                select(
                    DemandSignal.signal_type,
                    func.sum(DemandSignal.value)
                )
                .where(DemandSignal.sku_id == sku_id)
                .where(DemandSignal.tenant_id == tenant_id)
                .group_by(DemandSignal.signal_type)
            )

            demand_rows = demand_result.all()

            demand_data = {row[0]: row[1] for row in demand_rows}

            views = int(demand_data.get("views", 0))
            add_to_cart = int(demand_data.get("add_to_cart", 0))
            purchases = int(demand_data.get("purchases", 0))

            # -----------------------------------------
            # 3. Skip rows with no useful data
            # -----------------------------------------
            if views == 0 and add_to_cart == 0 and purchases == 0:
                continue

            # -----------------------------------------
            # 4. Build dataset row
            # -----------------------------------------
            dataset.append({
                "sku_id": sku_id,
                "avg_competitor_price": avg_price,
                "min_competitor_price": min_price,
                "max_competitor_price": max_price,
                "views": views,
                "add_to_cart": add_to_cart,
                "target_demand": purchases
            })

        return dataset