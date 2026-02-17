from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.demand_signal import DemandSignal

router = APIRouter(prefix="/analytics/demand", tags=["Demand Analytics"])


@router.get("/{sku_id}")
async def get_demand_analytics(
    sku_id: int,
    tenant_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns demand funnel analytics for a SKU
    """

    # -------------------------------
    # Aggregate demand signals
    # -------------------------------
    result = await db.execute(
        select(
            DemandSignal.signal_type,
            func.sum(DemandSignal.value)
        )
        .where(DemandSignal.sku_id == sku_id)
        .where(DemandSignal.tenant_id == tenant_id)
        .group_by(DemandSignal.signal_type)
    )

    rows = result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No demand data found")

    # -------------------------------
    # Map signals
    # -------------------------------
    views = 0
    add_to_cart = 0
    purchases = 0

    for signal_type, value in rows:
        if signal_type == "views":
            views = value
        elif signal_type == "add_to_cart":
            add_to_cart = value
        elif signal_type == "purchases":
            purchases = value

    # -------------------------------
    # Derived metrics
    # -------------------------------
    ctr = (add_to_cart / views * 100) if views > 0 else 0
    conversion_rate = (purchases / views * 100) if views > 0 else 0
    cart_conversion = (purchases / add_to_cart * 100) if add_to_cart > 0 else 0

    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,
        "views": views,
        "add_to_cart": add_to_cart,
        "purchases": purchases,
        "ctr_percent": round(ctr, 2),
        "conversion_rate_percent": round(conversion_rate, 2),
        "cart_conversion_percent": round(cart_conversion, 2)
    }