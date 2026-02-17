from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.services.feature_service import FeatureService
from app.services.ml_model import DemandModelService
from app.services.pricing_engine import PricingEngine

router = APIRouter(prefix="/analytics/ab-test", tags=["A/B Testing"])


@router.get("/{sku_id}")
async def run_ab_test(
    sku_id: int,
    tenant_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare base price vs AI recommended price
    """

    # ----------------------------
    # 1. Fetch SKU
    # ----------------------------
    result = await db.execute(
        select(SKU)
        .where(SKU.id == sku_id)
        .where(SKU.tenant_id == tenant_id)
    )
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    # ----------------------------
    # 2. Get Features
    # ----------------------------
    features = await FeatureService.get_features(
        db=db,
        sku_id=sku_id,
        tenant_id=tenant_id
    )

    # ----------------------------
    # 3. Predict demand
    # ----------------------------
    predicted_demand = DemandModelService.predict(tenant_id, features)

    # ----------------------------
    # 4. Strategy A → Base Price
    # ----------------------------
    base_price = float(sku.base_price)
    cost_price = float(sku.cost_price)

    base_revenue = base_price * predicted_demand
    base_profit = (base_price - cost_price) * predicted_demand

    # ----------------------------
    # 5. Strategy B → AI Price
    # ----------------------------
    pricing_result = PricingEngine.calculate_price(
        cost_price=cost_price,
        base_price=base_price,
        predicted_demand=predicted_demand,
        avg_comp_price=features["avg_competitor_price"],
        min_comp_price=features["min_competitor_price"],
        max_comp_price=features["max_competitor_price"],
    )

    ai_price = pricing_result["recommended_price"]

    ai_revenue = ai_price * predicted_demand
    ai_profit = (ai_price - cost_price) * predicted_demand

    # ----------------------------
    # 6. Decide Winner
    # ----------------------------
    if ai_profit > base_profit:
        winner = "AI_PRICE"
    else:
        winner = "BASE_PRICE"

    uplift_revenue = ai_revenue - base_revenue
    uplift_profit = ai_profit - base_profit

    # ----------------------------
    # 7. Response
    # ----------------------------
    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,

        "predicted_demand": round(predicted_demand, 2),

        "strategy_A": {
            "name": "Base Price",
            "price": base_price,
            "revenue": round(base_revenue, 2),
            "profit": round(base_profit, 2)
        },

        "strategy_B": {
            "name": "AI Price",
            "price": ai_price,
            "revenue": round(ai_revenue, 2),
            "profit": round(ai_profit, 2)
        },

        "uplift": {
            "revenue_diff": round(uplift_revenue, 2),
            "profit_diff": round(uplift_profit, 2)
        },

        "winner": winner,
        "recommendation": "Use AI price" if winner == "AI_PRICE" else "Keep base price"
    }