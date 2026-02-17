from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.feature_service import FeatureService
from app.services.explainability_service import ExplainabilityService

router = APIRouter(prefix="/ml", tags=["ML Explainability"])


@router.get("/explain-demand/{sku_id}")
async def explain_demand(
    sku_id: int,
    tenant_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):

    # 1. Get features
    features = await FeatureService.get_features(
        db=db,
        sku_id=sku_id,
        tenant_id=tenant_id
    )

    if not features:
        raise HTTPException(status_code=404, detail="Features not found")

    # 2. Explain prediction
    result = ExplainabilityService.explain_demand(
        tenant_id=tenant_id,
        features=features
    )

    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,
        **result
    }