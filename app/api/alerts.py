from fastapi import APIRouter, Depends, HTTPException
from app.core.tenant import get_tenant_id
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sku import SKU
from app.services.feature_service import FeatureService
from app.services.ml_model import DemandModelService
from app.services.pricing_engine import PricingEngine

router = APIRouter(prefix="/analytics/alerts", tags=["Alerts"])


@router.get("/{sku_id}")
async def get_alerts(
    sku_id: int,
    tenant_id: int = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    # ----------------------------
    # 1. Fetch SKU
    # ----------------------------
    result = await db.execute(
        select(SKU)
        .where(SKU.id == sku_id)
        .where(SKU.tenant_id == tenant_id)
    )
    sku = result.scalar_one_or_none()

    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    cost_price = float(sku.cost_price)
    base_price = float(sku.base_price)

    # ----------------------------
    # 2. Features
    # ----------------------------
    features = await FeatureService.get_features(
        db=db,
        sku_id=sku_id,
        tenant_id=tenant_id
    )

    # Safe extraction (avoid KeyError crashes)
    avg_comp_price = features.get("avg_competitor_price", 0)
    min_comp_price = features.get("min_competitor_price", 0)
    max_comp_price = features.get("max_competitor_price", 0)

    # ----------------------------
    # 3. Demand prediction
    # ----------------------------
    predicted_demand = DemandModelService.predict(tenant_id, features)

    # ----------------------------
    # 4. Recommended price
    # ----------------------------
    pricing_result = PricingEngine.calculate_price(
        cost_price=cost_price,
        base_price=base_price,
        predicted_demand=predicted_demand,
        avg_comp_price=avg_comp_price,
        min_comp_price=min_comp_price,
        max_comp_price=max_comp_price,
    )

    recommended_price = pricing_result["recommended_price"]

    # ----------------------------
    # 5. Margin calculation
    # ----------------------------
    margin_percent = 0
    if cost_price > 0:
        margin_percent = ((recommended_price - cost_price) / cost_price) * 100

    # ----------------------------
    # 6. Alert Logic
    # ----------------------------
    alerts = []

    # Margin safety threshold
    min_allowed_price = cost_price * 1.10

    if recommended_price < min_allowed_price:
        alerts.append({
            "type": "LOW_MARGIN_RISK",
            "message": "Recommended price is too close to cost",
            "severity": "HIGH"
        })

    # Competitor undercut alert
    if min_comp_price and recommended_price > min_comp_price:
        alerts.append({
            "type": "COMPETITOR_UNDERCUT",
            "message": "Competitor is selling cheaper than us",
            "severity": "MEDIUM"
        })

    # Overpricing risk
    if max_comp_price and recommended_price > max_comp_price * 1.25:
        alerts.append({
            "type": "OVERPRICED_RISK",
            "message": "Price is significantly higher than competitors",
            "severity": "HIGH"
        })

    # High demand opportunity
    if predicted_demand > 30:
        alerts.append({
            "type": "HIGH_DEMAND_OPPORTUNITY",
            "message": "Demand is high — consider increasing price",
            "severity": "HIGH"
        })

    # Low demand warning
    if predicted_demand < 5:
        alerts.append({
            "type": "LOW_DEMAND_WARNING",
            "message": "Demand is very low — consider discounting",
            "severity": "MEDIUM"
        })

    # ----------------------------
    # 7. Response
    # ----------------------------
    return {
        "sku_id": sku_id,
        "tenant_id": tenant_id,
        "recommended_price": round(recommended_price, 2),
        "predicted_demand": round(predicted_demand, 2),
        "margin_percent": round(margin_percent, 2),
        "alerts": alerts
    }