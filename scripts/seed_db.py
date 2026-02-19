import asyncio

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

        # avoid duplicate seed
        existing = await db.get(Tenant, 1)
        if existing:
            print("Seed already exists, skipping...")
            return

        tenant = Tenant(id=1, name="Demo Tenant")

        product = Product(
            id=1,
            name="Test Product",
            sku="TEST-001",
            tenant_id=1
        )

        sku = SKU(
            id=1,
            tenant_id=1,
            product_id=1,
            name="Test SKU",
            variant="Default",
            cost_price=100,
            base_price=150
        )

        rl = PricingRLState(
            tenant_id=1,
            sku_id=1,
            avg_reward=0.0,
            total_trials=0,
            epsilon=0.2
        )

        db.add_all([tenant, product, sku, rl])
        await db.commit()

        print(" Database seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed())