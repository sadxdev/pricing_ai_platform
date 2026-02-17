from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.tenant import get_tenant_id
from sqlalchemy import select

from app.db.session import get_db
from app.models.product import Product

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/")
async def create_product(
    name: str,
    sku: str,
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:

    product = Product(
        name=name,
        sku=sku,
        tenant_id=tenant_id
    )

    db.add(product)

    try:
        await db.commit()
        await db.refresh(product)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="SKU already exists"
        )

    return {
        "message": "product created",
        "id": str(product.id)
    }

@router.get("/")
async def list_products(
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:

    result = await db.execute(
        select(Product).where(Product.tenant_id == tenant_id)
    )

    products = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
        }
        for p in products
    ]