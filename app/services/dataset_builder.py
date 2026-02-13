from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sku import SKU
from app.services.feature_service import FeatureService


class DatasetBuilder:

    @staticmethod
    async def build_training_dataset(db: AsyncSession) -> list[dict]:

        dataset = []

        # get all SKUs
        result = await db.execute(select(SKU))
        skus = result.scalars().all()

        for sku in skus:
            features = await FeatureService.get_features(db, sku.id)

            row = {
                "sku_id": sku.id,
                "avg_competitor_price": features["avg_competitor_price"],
                "min_competitor_price": features["min_competitor_price"],
                "max_competitor_price": features["max_competitor_price"],
                "views": features["views"],
                "add_to_cart": features["add_to_cart"],
                "purchases": features["purchases"],
                "target_demand": features["purchases"],  # supervised label
            }

            dataset.append(row)

        return dataset