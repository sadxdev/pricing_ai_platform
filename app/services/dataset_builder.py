from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.sku import SKU
from app.models.competitor_price import CompetitorPrice
from app.models.demand_signal import DemandSignal


class DatasetBuilder:

    @staticmethod
    async def build_dataset(
        db: AsyncSession,
        tenant_id: int
    ) -> list[dict]:
        """
        Build ML dataset for a given tenant.
        Each row = one SKU with aggregated features
        """

        # -------------------------------
        # Step 1: Get all SKUs for tenant
        # -------------------------------
        sku_query = await db.execute(
            select(SKU).where(SKU.tenant_id == tenant_id)
        )
        skus = sku_query.scalars().all()

        dataset = []

        # -------------------------------
        # Step 2: For each SKU gather features
        # -------------------------------
        for sku in skus:

            sku_id = sku.id

            # ---- Competitor price aggregation ----
            comp_query = await db.execute(
                select(
                    func.avg(CompetitorPrice.competitor_price),
                    func.min(CompetitorPrice.competitor_price),
                    func.max(CompetitorPrice.competitor_price),
                )
                .where(
                    CompetitorPrice.sku_id == sku_id,
                    CompetitorPrice.tenant_id == tenant_id
                )
            )

            comp_row = comp_query.first()

            if comp_row:
                avg_price, min_price, max_price = comp_row
            else:
                avg_price = min_price = max_price = 0

            avg_price = float(avg_price or 0)
            min_price = float(min_price or 0)
            max_price = float(max_price or 0)

            # ---- Demand aggregation ----
            demand_query = await db.execute(
                select(
                    DemandSignal.signal_type,
                    func.sum(DemandSignal.value)
                )
                .where(
                    DemandSignal.sku_id == sku_id,
                    DemandSignal.tenant_id == tenant_id
                )
                .group_by(DemandSignal.signal_type)
            )

            demand_rows = demand_query.all()
            demand_data = {row[0]: row[1] for row in demand_rows}

            views = demand_data.get("views", 0)
            add_to_cart = demand_data.get("add_to_cart", 0)
            purchases = demand_data.get("purchases", 0)

            # ---- Final dataset row ----
            dataset.append({
                "sku_id": sku_id,
                "cost_price": float(sku.cost_price),
                "base_price": float(sku.base_price),
                "avg_competitor_price": avg_price,
                "min_competitor_price": min_price,
                "max_competitor_price": max_price,
                "views": views,
                "add_to_cart": add_to_cart,
                "purchases": purchases,
            })

        return dataset