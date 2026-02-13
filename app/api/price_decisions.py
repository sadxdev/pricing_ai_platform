from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.deps import get_db
from app.models.price_decision import PriceDecision
from app.models.sku import SKU

router = APIRouter(prefix="/price-decisions", tags=["Price Decisions"])


# Create price decision
@router.post("/")
async def create_price_decision(
    sku_id: int,
    recommended_price: float,
    strategy: str,
    reason: str,
    model_version: str,
    db: AsyncSession = Depends(get_db),
) -> dict:

    # validate SKU exists
    result = await db.execute(select(SKU).where(SKU.id == sku_id))
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    record = PriceDecision(
        sku_id=sku_id,
        recommended_price=recommended_price,
        strategy=strategy,
        reason=reason,
        model_version=model_version,
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {"id": record.id, "message": "price decision recorded"}


# list price decisions
@router.get("/")
async def list_price_decisions(
    db: AsyncSession = Depends(get_db),
) -> list[dict]:

    result = await db.execute(select(PriceDecision))
    rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "sku_id": r.sku_id,
            "recommended_price": float(r.recommended_price),
            "strategy": r.strategy,
            "reason": r.reason,
            "model_version": r.model_version,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]