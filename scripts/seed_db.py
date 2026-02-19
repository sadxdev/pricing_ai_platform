import asyncio
from datetime import datetime
from sqlalchemy import select

from app.db.session import async_session

# import ALL models so SQLAlchemy registry is complete
from app.models.tenant import Tenant
from app.models.product import Product
from app.models.sku import SKU
from app.models.demand_signal import DemandSignal
from app.models.price_decision import PriceDecision
from app.models.competitor_price import CompetitorPrice
from app.models.pricing_rl_state import PricingRLState


async def seed():
    async with async_session() as db:

        # -----------------------------
        # Tenant
        # -----------------------------
        existing_tenant = await db.get(Tenant, 1)
        if not existing_tenant:
            db.add(Tenant(id=1, name="Demo Tenant"))
            await db.commit()
            print("Tenant seeded")
        else:
            print("Tenant already exists, skipping")

        # -----------------------------
        # Product
        # -----------------------------
        existing_product = await db.get(Product, 1)
        if not existing_product:
            db.add(Product(
                id=1,
                name="Test Product",
                sku="TEST-001",
                tenant_id=1
            ))
            await db.commit()
            print("Product seeded")
        else:
            print("Product already exists, skipping")

        # -----------------------------
        # SKU
        # -----------------------------
        existing_sku = await db.get(SKU, 1)
        if not existing_sku:
            db.add(SKU(
                id=1,
                tenant_id=1,
                product_id=1,
                name="Test SKU",
                variant="Default",
                cost_price=100,
                base_price=150
            ))
            await db.commit()
            print("SKU seeded")
        else:
            print("SKU already exists, skipping")

        # -----------------------------
        # RL State
        # -----------------------------
        rl_result = await db.execute(
            select(PricingRLState)
            .where(PricingRLState.tenant_id == 1)
            .where(PricingRLState.sku_id == 1)
        )
        existing_rl = rl_result.scalar_one_or_none()
        if not existing_rl:
            db.add(PricingRLState(
                tenant_id=1,
                sku_id=1,
                avg_reward=0.0,
                total_trials=0,
                epsilon=0.2
            ))
            await db.commit()
            print("RL State seeded")
        else:
            print("RL State already exists, skipping")

        # -----------------------------
        # Price Decision
        # -----------------------------
        pd_result = await db.execute(
            select(PriceDecision)
            .where(PriceDecision.sku_id == 1)
            .where(PriceDecision.tenant_id == 1)
        )
        existing_pd = pd_result.scalar_one_or_none()
        if not existing_pd:
            db.add(PriceDecision(
                sku_id=1,
                tenant_id=1,
                recommended_price=180.00,
                base_price=150.00,
                cost_price=100.00,
                strategy="competitive",
                reason="Seed data",
                predicted_demand=50,
                created_at=datetime.utcnow()
            ))
            await db.commit()
            print("Price Decision seeded")
        else:
            print("Price Decision already exists, skipping")

        # -----------------------------
        # Demand Signals
        # -----------------------------
        ds_result = await db.execute(
            select(DemandSignal)
            .where(DemandSignal.sku_id == 1)
            .where(DemandSignal.tenant_id == 1)
        )
        existing_ds = ds_result.scalars().all()
        if not existing_ds:
            db.add_all([
                DemandSignal(sku_id=1, tenant_id=1, signal_type="views",
                             value=1000, created_at=datetime.utcnow()),
                DemandSignal(sku_id=1, tenant_id=1, signal_type="add_to_cart",
                             value=200, created_at=datetime.utcnow()),
                DemandSignal(sku_id=1, tenant_id=1, signal_type="purchases",
                             value=50, created_at=datetime.utcnow()),
            ])
            await db.commit()
            print("Demand Signals seeded")
        else:
            print("Demand Signals already exist, skipping")

        print("Database seed complete")


if __name__ == "__main__":
    asyncio.run(seed())