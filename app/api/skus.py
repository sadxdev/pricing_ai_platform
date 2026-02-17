from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/skus", tags=["SKUs"])


# Create SKU
@router.post("/")
async def create_sku(
    product_id: int,
    name: str,
    variant: str,
    cost_price: float,
    base_price: float,
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    sku = SKU(
        product_id=product_id,
        name=name,
        variant=variant,
        cost_price=cost_price,
        base_price=base_price,
        tenant_id=tenant_id,
    )

    db.add(sku)

    try:
        await db.commit()
        await db.refresh(sku)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="SKU already exists")

    return {"id": sku.id}


# List SKUs
@router.get("/")
async def list_skus(
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SKU).where(SKU.tenant_id == tenant_id)
    )

    skus = result.scalars().all()

    return [
        {
            "id": s.id,
            "name": s.name,
            "variant": s.variant,
            "base_price": float(s.base_price),
        }
        for s in skus
    ]

@router.get("/{sku_id}")
async def get_sku(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SKU).where(
            SKU.id == sku_id,
            SKU.tenant_id == tenant_id
        )
    )

    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    return {
        "id": sku.id,
        "name": sku.name,
        "variant": sku.variant,
        "base_price": float(sku.base_price),
    }

@router.delete("/{sku_id}")
async def delete_sku(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SKU).where(
            SKU.id == sku_id,
            SKU.tenant_id == tenant_id
        )
    )

    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    await db.delete(sku)
    await db.commit()

    return {"message": "deleted"}

