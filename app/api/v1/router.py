from fastapi import APIRouter

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
from app.api.revenue import router as revenue_router
from app.api.ab_testing import router as ab_testing_router
from app.api.alerts import router as alerts_router
from app.api.ml_monitoring import router as ml_monitoring_router
from app.api.optimization import router as optimization_router
from app.api.auto_pricing import router as auto_pricing_router
from app.api.pricing_rl import router as rl_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(product_router)
v1_router.include_router(sku_router)
v1_router.include_router(competitor_router)
v1_router.include_router(demand_router)
v1_router.include_router(decision_router)
v1_router.include_router(feature_router)
v1_router.include_router(dataset_router)
v1_router.include_router(ml_router)
v1_router.include_router(pricing_router)
v1_router.include_router(price_history_router)
v1_router.include_router(explain_router)
v1_router.include_router(margin_router)
v1_router.include_router(demand_analytics_router)
v1_router.include_router(ml_explain_router)
v1_router.include_router(revenue_router)
v1_router.include_router(ab_testing_router)
v1_router.include_router(alerts_router)
v1_router.include_router(ml_monitoring_router)
v1_router.include_router(optimization_router)
v1_router.include_router(auto_pricing_router)
v1_router.include_router(rl_router)