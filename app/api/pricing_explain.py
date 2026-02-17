from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.services.feature_service import FeatureService
from app.services.ml_model import DemandModelService
from app.services.pricing_engine import PricingEngine

router = APIRouter(prefix="/pricing-explain", tags=["Pricing Explain"])


@router.get("/{sku_id}")
async def explain_price(
    sku_id: int,
    tenant_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # -----------------------------------
    # 1. Get SKU
    # -----------------------------------
    result = await db.execute(
        select(SKU)
        .where(SKU.id == sku_id)
        .where(SKU.tenant_id == tenant_id)
    )
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    # -----------------------------------
    # 2. Get Features
    # -----------------------------------
    features = await FeatureService.get_features(
        db=db,
        sku_id=sku_id,
        tenant_id=tenant_id
    )

    # -----------------------------------
    # 3. Predict Demand
    # -----------------------------------
    predicted_demand = DemandModelService.predict(
        tenant_id,
        features
    )

    # -----------------------------------
    # 4. Pricing Engine
    # -----------------------------------
    pricing = PricingEngine.calculate_price(
        cost_price=float(sku.cost_price),
        base_price=float(sku.base_price),
        predicted_demand=predicted_demand,
        avg_comp_price=features["avg_competitor_price"],
        min_comp_price=features["min_competitor_price"],
        max_comp_price=features["max_competitor_price"],
    )

    # -----------------------------------
    # 5. Build Explainable Output
    # -----------------------------------
    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,

        "inputs": {
            "cost_price": float(sku.cost_price),
            "base_price": float(sku.base_price),
            "predicted_demand": predicted_demand,
            "avg_comp_price": features["avg_competitor_price"],
            "min_comp_price": features["min_competitor_price"],
            "max_comp_price": features["max_competitor_price"],
            "views": features["views"],
            "add_to_cart": features["add_to_cart"],
        },

        "decision": pricing["recommended_price"],

        "explanation": {
            "demand_signal": predicted_demand,
            "competitor_anchor": features["min_competitor_price"],
            "price_floor": pricing["min_allowed_price"],
        }
    }