from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.pricing_rl_agent import PricingRLAgent

router = APIRouter(prefix="/rl", tags=["Reinforcement Learning"])


@router.post("/reward")
async def update_reward(
    tenant_id: int = Query(...),
    sku_id: int = Query(...),
    revenue: float = Query(...),
    db: AsyncSession = Depends(get_db)
):
    await PricingRLAgent.update_reward(
        db=db,
        tenant_id=tenant_id,
        sku_id=sku_id,
        reward=revenue
    )

    return {"status": "reward updated"}