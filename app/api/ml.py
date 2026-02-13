from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.ml_model import DemandModelService
from app.services.feature_service import FeatureService

router = APIRouter(prefix="/ml", tags=["ML"])


# -----------------------------
# TRAIN MODEL
# -----------------------------
@router.post("/train")
async def train_model(db: AsyncSession = Depends(get_db)):
    result = await DemandModelService.train_model(db)
    return result


# -----------------------------
# PREDICT DEMAND
# -----------------------------
@router.get("/predict/{sku_id}")
async def predict_demand(sku_id: int, db: AsyncSession = Depends(get_db)):
    # get features first
    features = await FeatureService.get_features(db, sku_id)

    prediction = DemandModelService.predict(features)

    return {
        "sku_id": sku_id,
        "predicted_demand": prediction,
        "features_used": features
    }