from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.product import Product

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/")
async def create_product(
    name: str,
    sku: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    product = Product(name=name, sku=sku)

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

    return {"message": "product created", "id": str(product.id)}

@router.get("/")
async def list_products(
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(
        Product.__table__.select()
    )
    rows = result.fetchall()

    return [
        {"id": row.id, "name": row.name, "sku": row.sku}
        for row in rows
    ]