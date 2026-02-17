from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.services.feature_service import FeatureService
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/features", tags=["Features"])


@router.get("/{sku_id}")
async def get_features(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),   # 👈 Inject tenant
    db: AsyncSession = Depends(get_db),
):
    return await FeatureService.get_features(db, sku_id, tenant_id)