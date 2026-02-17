from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.tenant import get_tenant_id

from app.services.ml_model import DemandModelService
from app.services.feature_service import FeatureService


router = APIRouter(prefix="/ml", tags=["ML"])


# ---------------------------------------------
# TRAIN MODEL ENDPOINT
# ---------------------------------------------
@router.post("/train")
async def train_model(
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Train demand prediction model for a tenant
    """

    try:
        result = await DemandModelService.train_model(db, tenant_id)

        return {
            "message": "Model trained successfully",
            "tenant_id": tenant_id,
            "metrics": result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Training failed: {str(e)}"
        )


# ---------------------------------------------
# PREDICT DEMAND ENDPOINT
# ---------------------------------------------
@router.get("/predict/{sku_id}")
async def predict_demand(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Predict demand for a SKU (tenant isolated)
    """

    try:
        # Step 1: fetch features for SKU (tenant scoped)
        features = await FeatureService.get_features(
            db=db,
            sku_id=sku_id,
            tenant_id=tenant_id
        )

        # Step 2: predict demand using tenant model
        prediction = DemandModelService.predict(
            tenant_id=tenant_id,
            features=features
        )

        return {
            "tenant_id": tenant_id,
            "sku_id": sku_id,
            "predicted_demand": prediction,
            "features_used": features,
        }

    except ValueError as e:
        # model not trained or no data
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )