from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.services.feature_service import FeatureService

router = APIRouter(prefix="/features", tags=["Features"])


@router.get("/{sku_id}")
async def get_features(
    sku_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:

    # validate SKU exists
    result = await db.execute(select(SKU).where(SKU.id == sku_id))
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    features = await FeatureService.get_features(db, sku_id)

    return {
        "sku_id": sku_id,
        "features": features
    }