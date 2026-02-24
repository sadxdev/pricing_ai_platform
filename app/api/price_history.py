from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.tenant import get_tenant_id
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.models.price_decision import PriceDecision

router = APIRouter(prefix="/price-history", tags=["Price History"])


@router.get("/{sku_id}")
async def get_price_history(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(PriceDecision)
        .where(PriceDecision.sku_id == sku_id)
        .where(PriceDecision.tenant_id == tenant_id)
        .order_by(desc(PriceDecision.created_at))
        .limit(limit)
    )

    decisions = result.scalars().all()

    return [
        {
            "price": float(d.recommended_price),
            "base_price": float(d.base_price),
            "cost_price": float(d.cost_price),
            "predicted_demand": float(d.predicted_demand),
            "strategy": d.strategy,
            "created_at": d.created_at
        }
        for d in decisions
    ]