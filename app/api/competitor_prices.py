from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.competitor_price import CompetitorPrice
from app.models.sku import SKU

router = APIRouter(prefix="/competitor-prices", tags=["Competitor Prices"])


# Create competitor price
@router.post("/")
async def create_competitor_price(
    sku_id: int,
    competitor_name: str,
    competitor_price: float,
    db: AsyncSession = Depends(get_db),
) -> dict:

    # validate sku exists
    result = await db.execute(select(SKU).where(SKU.id == sku_id))
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    record = CompetitorPrice(
        sku_id=sku_id,
        competitor_name=competitor_name,
        competitor_price=competitor_price,
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {"id": record.id, "message": "competitor price added"}


# list competitor prices
@router.get("/")
async def list_competitor_prices(
    db: AsyncSession = Depends(get_db),
) -> list[dict]:

    result = await db.execute(select(CompetitorPrice))
    rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "sku_id": r.sku_id,
            "competitor_name": r.competitor_name,
            "competitor_price": float(r.competitor_price),
            "captured_at": r.captured_at.isoformat(),
        }
        for r in rows
    ]