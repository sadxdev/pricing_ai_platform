from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.price_decision import PriceDecision

router = APIRouter(prefix="/analytics/margin", tags=["Margin Analytics"])


@router.get("/{sku_id}")
async def margin_analytics(
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

    data = []

    for r in rows:
        margin = float(r.recommended_price - r.cost_price)
        margin_pct = (margin / float(r.cost_price)) * 100 if r.cost_price else 0

        data.append({
            "price": float(r.recommended_price),
            "cost": float(r.cost_price),
            "margin": round(margin, 2),
            "margin_percent": round(margin_pct, 2),
            "created_at": r.created_at
        })

    return data