from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.db.deps import get_db
from app.models.sku import SKU
from app.models.product import Product

router = APIRouter(prefix="/skus", tags=["SKUs"])


# Create SKU
@router.post("/")
async def create_sku(
    product_id: int,
    name: str,
    variant: str,
    cost_price: float,
    base_price: float,
    db: AsyncSession = Depends(get_db),
) -> dict:

    # check product exists
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sku = SKU(
        product_id=product_id,
        name=name,
        variant=variant,
        cost_price=cost_price,
        base_price=base_price,
    )

    db.add(sku)

    try:
        await db.commit()
        await db.refresh(sku)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="SKU creation failed")

    return {"id": sku.id, "message": "SKU created"}


# List SKUs
@router.get("/")
async def list_skus(
    db: AsyncSession = Depends(get_db),
) -> list[dict]:

    result = await db.execute(select(SKU))
    skus = result.scalars().all()

    return [
        {
            "id": sku.id,
            "product_id": sku.product_id,
            "name": sku.name,
            "variant": sku.variant,
            "cost_price": float(sku.cost_price),
            "base_price": float(sku.base_price),
        }
        for sku in skus
    ]