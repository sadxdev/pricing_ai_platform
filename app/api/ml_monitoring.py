from fastapi import APIRouter, Depends, HTTPException
from app.core.tenant import get_tenant_id

from app.services.ml_monitoring_service import MLMonitoringService

router = APIRouter(prefix="/analytics/ml-health", tags=["ML Monitoring"])


@router.get("")
async def get_model_health(tenant_id: int = Depends(get_tenant_id)):
    try:
        return MLMonitoringService.evaluate_model_health(tenant_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))