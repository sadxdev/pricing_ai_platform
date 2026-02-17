from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.price_decision import PriceDecision

router = APIRouter(prefix="/analytics/demand", tags=["Demand Analytics"])


@router.get("/{sku_id}")
async def demand_vs_price(
    sku_id: int,
    tenant_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(PriceDecision)
        .where(PriceDecision.sku_id == sku_id)
        .where(PriceDecision.tenant_id == tenant_id)
    )

    rows = result.scalars().all()

    return [
        {
            "price": float(r.recommended_price),
            "predicted_demand": float(r.predicted_demand),
            "created_at": r.created_at
        }
        for r in rows
    ]