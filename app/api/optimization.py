from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.tenant import get_tenant_id
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.services.feature_service import FeatureService
from app.services.price_optimizer import PriceOptimizer

router = APIRouter(prefix="/optimization", tags=["Optimization"])


@router.get("/optimize/{sku_id}")
async def optimize_price(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),
    objective: str = Query("profit"),
    db: AsyncSession = Depends(get_db)
):

    # 1. Fetch SKU
    result = await db.execute(
        select(SKU)
        .where(SKU.id == sku_id)
        .where(SKU.tenant_id == tenant_id)
    )
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    # 2. Features
    features = await FeatureService.get_features(
        db=db,
        sku_id=sku_id,
        tenant_id=tenant_id
    )

    # 3. Optimize
    result = PriceOptimizer.optimize_price(
        tenant_id=tenant_id,
        cost_price=float(sku.cost_price),
        base_price=float(sku.base_price),
        features=features,
        objective=objective
    )

    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,
        "base_price": float(sku.base_price),
        "cost_price": float(sku.cost_price),
        **result
    }