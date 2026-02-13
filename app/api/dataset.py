from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.dataset_builder import DatasetBuilder

router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.get("/training")
async def get_training_dataset(db: AsyncSession = Depends(get_db)):
    dataset = await DatasetBuilder.build_training_dataset(db)

    return {
        "total_rows": len(dataset),
        "data": dataset
    }