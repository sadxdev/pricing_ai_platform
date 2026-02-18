from sqlalchemy import Integer, ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base_class import Base


class CompetitorPrice(Base):
    __tablename__ = "competitor_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 🔐 Tenant Isolation
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # SKU reference
    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # Competitor info
    competitor_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    competitor_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        index=True
    )

    # Timestamp
    captured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    # Relationships
    sku = relationship("SKU", back_populates="competitor_prices")
    tenant = relationship("Tenant", back_populates="competitor_prices")
