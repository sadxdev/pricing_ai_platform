from fastapi import APIRouter, Depends, HTTPException
from app.core.tenant import get_tenant_id
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.price_decision import PriceDecision

router = APIRouter(prefix="/analytics/margin", tags=["Margin Analytics"])


@router.get("/{sku_id}")
async def get_margin_analytics(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns margin analytics for a SKU
    """

    # -------------------------------
    # Query all price decisions
    # -------------------------------
    result = await db.execute(
        select(
            PriceDecision.recommended_price,
            PriceDecision.cost_price,
            PriceDecision.predicted_demand
        )
        .where(PriceDecision.sku_id == sku_id)
        .where(PriceDecision.tenant_id == tenant_id)
    )

    rows = result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No pricing data found")

    margins = []
    profits = []

    for price, cost, demand in rows:
        if price == 0:
            continue

        margin_percent = ((price - cost) / price) * 100
        margin_value = (price - cost)

        margins.append(margin_percent)
        profits.append(margin_value * (demand or 1))

    if not margins:
        raise HTTPException(status_code=400, detail="Invalid data for margin calculation")

    # -------------------------------
    # Aggregate
    # -------------------------------
    avg_margin = sum(margins) / len(margins)
    min_margin = min(margins)
    max_margin = max(margins)

    avg_profit = sum(profits) / len(profits)
    total_profit = sum(profits)

    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,
        "avg_margin_percent": round(avg_margin, 2),
        "min_margin_percent": round(min_margin, 2),
        "max_margin_percent": round(max_margin, 2),
        "avg_profit_per_decision": round(avg_profit, 2),
        "total_profit_estimate": round(total_profit, 2),
        "data_points": len(rows)
    }