from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.tenant import get_tenant_id
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auto_pricing_agent import AutoPricingAgent

router = APIRouter(
    prefix="/auto-pricing",
    tags=["Auto Pricing Agent"]
)


@router.post("/run")
async def run_auto_pricing(
    tenant_id: int = Depends(get_tenant_id),
    objective: str = Query("profit"),
    db: AsyncSession = Depends(get_db)
):
    """
    Run auto pricing for all SKUs of a tenant
    """
    result = await AutoPricingAgent.run_for_tenant(
        db=db,
        tenant_id=tenant_id,
        objective=objective
    )

    return result