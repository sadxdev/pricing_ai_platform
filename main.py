from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine
from app.api.products import router as product_router
from app.api.skus import router as sku_router
from app.api.competitor_prices import router as competitor_router
from app.api.demand_signals import router as demand_router
from app.api.price_decisions import router as decision_router




app = FastAPI(title=settings.APP_NAME)
app.include_router(product_router)
app.include_router(sku_router)
app.include_router(competitor_router)
app.include_router(demand_router)
app.include_router(decision_router)

@app.on_event("startup")
async def startup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}