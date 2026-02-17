from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.services.feature_service import FeatureService
from app.services.ml_model import DemandModelService
from app.services.pricing_engine import PricingEngine
from app.services.pricing_service import PricingService   # ✅ ADD THIS

router = APIRouter(prefix="/pricing", tags=["Pricing"])


# ============================================================
# 🔹 RECOMMEND PRICE (ML + Feature + Engine)
# ============================================================
@router.get("/recommend/{sku_id}")
async def recommend_price(
    sku_id: int,
    tenant_id: int = int,
    db: AsyncSession = Depends(get_db)
):

    # ----------------------------
    # 1. Fetch SKU (tenant scoped)
    # ----------------------------
    result = await db.execute(
        select(SKU)
        .where(SKU.id == sku_id)
        .where(SKU.tenant_id == tenant_id)   # ✅ multi-tenant safety
    )
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    # ----------------------------
    # 2. Get Features (tenant scoped)
    # ----------------------------
    features = await FeatureService.get_features(
        db=db,
        sku_id=sku_id,
        tenant_id=tenant_id
    )

    # ----------------------------
    # 3. Predict Demand
    # ----------------------------
    predicted_demand = DemandModelService.predict(tenant_id, features)

    # ----------------------------
    # 4. Calculate Price
    # ----------------------------
    pricing_result = PricingEngine.calculate_price(
        cost_price=float(sku.cost_price),
        base_price=float(sku.base_price),
        predicted_demand=predicted_demand,
        avg_comp_price=features["avg_competitor_price"],
        min_comp_price=features["min_competitor_price"],
        max_comp_price=features["max_competitor_price"],
    )

    # ----------------------------
    # 5. Final Response
    # ----------------------------
    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,
        "product_id": sku.product_id,
        "predicted_demand": predicted_demand,
        "recommended_price": pricing_result["recommended_price"],
        "price_floor": pricing_result["min_allowed_price"],
        "base_price": float(sku.base_price),
        "cost_price": float(sku.cost_price),
        "features_used": features,
        "strategy": pricing_result["strategy"],
        "optimized_price": pricing_result["optimized_price"],
        "expected_profit": pricing_result["expected_profit"],
    }


# ============================================================
# 🔹 SIMPLE PRICE CALCULATOR (Service Wrapper)
# ============================================================
@router.get("/calculate/{sku_id}")
async def calculate_price(
    sku_id: int,
    tenant_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await PricingService.calculate_price(
            db=db,
            sku_id=sku_id,
            tenant_id=tenant_id
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))