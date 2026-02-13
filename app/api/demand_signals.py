from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.deps import get_db
from app.models.demand_signal import DemandSignal
from app.models.sku import SKU

router = APIRouter(prefix="/demand-signals", tags=["Demand Signals"])


# Create demand signal
@router.post("/")
async def create_demand_signal(
    sku_id: int,
    signal_type: str,
    value: int,
    db: AsyncSession = Depends(get_db),
) -> dict:

    # validate SKU exists
    result = await db.execute(select(SKU).where(SKU.id == sku_id))
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    record = DemandSignal(
        sku_id=sku_id,
        signal_type=signal_type,
        value=value,
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {"id": record.id, "message": "demand signal added"}


# List demand signals
@router.get("/")
async def list_demand_signals(
    db: AsyncSession = Depends(get_db),
) -> list[dict]:

    result = await db.execute(select(DemandSignal))
    rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "sku_id": r.sku_id,
            "signal_type": r.signal_type,
            "value": r.value,
            "captured_at": r.captured_at.isoformat(),
        }
        for r in rows
    ]