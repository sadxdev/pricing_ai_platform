import app.db.base_class

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine

# Import routers
from app.api.products import router as product_router
from app.api.skus import router as sku_router
from app.api.competitor_prices import router as competitor_router
from app.api.demand_signals import router as demand_router
from app.api.price_decisions import router as decision_router
from app.api.features import router as feature_router
from app.api.dataset import router as dataset_router
from app.api.ml import router as ml_router
from app.api.pricing import router as pricing_router
from app.api.price_history import router as price_history_router
from app.api.pricing_explain import router as explain_router
from app.api.margin_analytics import router as margin_router
from app.api.demand_analytics import router as demand_analytics_router
from app.api.ml_explain import router as ml_explain_router
from app.api.analytics.revenue import router as revenue_router
from app.api.ab_testing import router as ab_testing_router
from app.api.alerts import router as alerts_router
from app.api.ml_monitoring import router as ml_monitoring_router
from app.api.optimization import router as optimization_router
from app.api.auto_pricing import router as auto_pricing_router
from app.api.pricing_rl import router as rl_router
from app.api.analytics import router as analytics_router





# CREATE APP FIRST
app = FastAPI(title=settings.APP_NAME)

# THEN REGISTER ROUTERS
app.include_router(product_router)
app.include_router(sku_router)
app.include_router(competitor_router)
app.include_router(demand_router)
app.include_router(decision_router)
app.include_router(feature_router)
app.include_router(dataset_router)
app.include_router(ml_router)
app.include_router(pricing_router)
app.include_router(price_history_router)
app.include_router(explain_router)
app.include_router(margin_router)
app.include_router(demand_analytics_router)
app.include_router(ml_explain_router)
app.include_router(revenue_router)
app.include_router(ab_testing_router)
app.include_router(alerts_router)
app.include_router(ml_monitoring_router)
app.include_router(optimization_router)
app.include_router(auto_pricing_router)
app.include_router(rl_router)
app.include_router(analytics_router)


# Allow frontend origin
origins = [
    "http://localhost:3000",  # Next.js dev
    # "https://yourdomain.com"  # Add in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------
# Startup DB
# --------------------------------------
@app.on_event("startup")
async def startup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)

# --------------------------------------
# Health
# --------------------------------------
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}