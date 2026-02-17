from sqlalchemy import Integer, ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


class PriceDecision(Base):
    __tablename__ = "price_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 🔥 Multi-tenant support
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # 💰 Pricing Data
    recommended_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # 📈 ML data
    predicted_demand: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # 🧠 Strategy metadata
    strategy: Mapped[str] = mapped_column(String(100))
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    # 🔗 Relationships
    sku = relationship("SKU", back_populates="price_decisions")
    tenant = relationship("Tenant", backref="price_decisions")