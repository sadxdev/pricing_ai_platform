from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine
from app.api.products import router as product_router
from app.api.skus import router as sku_router
from app.api.competitor_prices import router as competitor_router
from app.api.demand_signals import router as demand_router
from app.api.price_decisions import router as decision_router
from app.api.features import router as feature_router
from app.api.dataset import router as dataset_router
from app.api.ml import router as ml_router
from app.api.pricing import router as pricing_router
import app.db.base_class

app = FastAPI(title=settings.APP_NAME)
app.include_router(product_router)
app.include_router(sku_router)
app.include_router(competitor_router)
app.include_router(demand_router)
app.include_router(decision_router)
app.include_router(feature_router)
app.include_router(dataset_router)
app.include_router(ml_router)
app.include_router(pricing_router)

@app.on_event("startup")
async def startup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}