from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.analytics.revenue_service import RevenueAnalyticsService

router = APIRouter(prefix="/analytics/revenue", tags=["Revenue Analytics"])


@router.get("/{sku_id}")
async def get_revenue_analytics(
    sku_id: int,
    tenant_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await RevenueAnalyticsService.get_revenue_metrics(
            db=db,
            sku_id=sku_id,
            tenant_id=tenant_id
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))