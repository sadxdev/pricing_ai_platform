import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

from main import app
from app.db.session import get_db
from app.core.auth import get_current_user
from app.db.base_class import Base

load_dotenv()

# -----------------------------
# Test Database
# -----------------------------
TEST_DATABASE_URL = "postgresql+asyncpg://pricing_user:pricing_pass@postgres:5432/pricing_test_db"

# We will initialize these inside the event loop (IMPORTANT)
test_engine = None
test_session_maker = None


# -----------------------------
# Mock JWT user — no Keycloak needed
# -----------------------------
MOCK_USER = {
    "sub": "test-user-id",
    "tenant_id": 1,
    "preferred_username": "testuser",
    "email": "testuser@example.com"
}


# -----------------------------
# Override get_current_user
# -----------------------------
async def mock_get_current_user():
    return MOCK_USER


# -----------------------------
# Override get_db with test DB
# -----------------------------
async def override_get_db():
    async with test_session_maker() as session:
        yield session


# -----------------------------
# Create & drop tables (FIXED event loop issue)
# -----------------------------
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    global test_engine
    global test_session_maker

    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# -----------------------------
# Seed test data
# -----------------------------
@pytest_asyncio.fixture(scope="function")
async def seed_test_db(setup_test_db):
    from app.models.tenant import Tenant
    from app.models.product import Product
    from app.models.sku import SKU
    from app.models.price_decision import PriceDecision
    from app.models.demand_signal import DemandSignal
    from datetime import datetime
    from sqlalchemy import text

    async with test_session_maker() as db:
        # 🔥 CLEAR existing data first (important)
        await db.execute(text("TRUNCATE TABLE demand_signals RESTART IDENTITY CASCADE"))
        await db.execute(text("TRUNCATE TABLE price_decisions RESTART IDENTITY CASCADE"))
        await db.execute(text("TRUNCATE TABLE skus RESTART IDENTITY CASCADE"))
        await db.execute(text("TRUNCATE TABLE products RESTART IDENTITY CASCADE"))
        await db.execute(text("TRUNCATE TABLE tenants RESTART IDENTITY CASCADE"))
        await db.commit()

        # -----------------------------
        # Seed fresh data
        # -----------------------------
        db.add(Tenant(id=1, name="Test Tenant"))
        await db.commit()

        db.add(Product(id=1, name="Test Product", sku="TEST-001", tenant_id=1))
        await db.commit()

        db.add(SKU(
            id=1, tenant_id=1, product_id=1,
            name="Test SKU", variant="Default",
            cost_price=100, base_price=150
        ))
        await db.commit()

        db.add(PriceDecision(
            sku_id=1, tenant_id=1,
            recommended_price=180.00,
            base_price=150.00,
            cost_price=100.00,
            strategy="competitive",
            reason="Test seed",
            predicted_demand=50,
            created_at=datetime.utcnow()
        ))
        await db.commit()

        db.add_all([
            DemandSignal(
                sku_id=1, tenant_id=1,
                signal_type="views", value=1000,
                created_at=datetime.utcnow()
            ),
            DemandSignal(
                sku_id=1, tenant_id=1,
                signal_type="add_to_cart", value=200,
                created_at=datetime.utcnow()
            ),
            DemandSignal(
                sku_id=1, tenant_id=1,
                signal_type="purchases", value=50,
                created_at=datetime.utcnow()
            ),
        ])
        await db.commit()


# -----------------------------
# HTTP client fixture
# -----------------------------
@pytest_asyncio.fixture(scope="function")
async def client(seed_test_db):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()