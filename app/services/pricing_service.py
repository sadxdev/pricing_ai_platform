from sqlalchemy.ext.asyncio import AsyncSession

from app.services.feature_service import FeatureService
from app.services.pricing_engine import PricingEngine
from app.models.sku import SKU


class PricingService:

    @staticmethod
    async def calculate_price(
        db: AsyncSession,
        sku_id: int,
        tenant_id: int
    ) -> dict:

        # 1️⃣ Fetch SKU
        sku = await db.get(SKU, sku_id)

        if not sku:
            raise ValueError("SKU not found")

        # 2️⃣ Get feature data (competitor + demand)
        features = await FeatureService.get_features(
            db=db,
            sku_id=sku_id,
            tenant_id=tenant_id
        )

        # 3️⃣ Predict demand (simple rule for now)
        predicted_demand = (
            features["views"] * 0.1 +
            features["add_to_cart"] * 0.5 +
            features["purchases"] * 1.5
        )

        # 4️⃣ Run pricing engine
        result = PricingEngine.calculate_price(
            cost_price=float(sku.cost_price),
            base_price=float(sku.base_price),
            predicted_demand=predicted_demand,
            avg_comp_price=features["avg_competitor_price"],
            min_comp_price=features["min_competitor_price"],
            max_comp_price=features["max_competitor_price"],
        )

        return result