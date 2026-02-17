from sqlalchemy import String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SKU(Base):
    __tablename__ = "skus"

    # -----------------------------
    # Primary Key
    # -----------------------------
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # -----------------------------
    # Tenant (Multi-tenant support)
    # -----------------------------
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # -----------------------------
    # Product Relationship
    # -----------------------------
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # -----------------------------
    # SKU Details
    # -----------------------------
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Example: size / color variant
    variant: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # -----------------------------
    # Pricing Fields
    # -----------------------------
    cost_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    base_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # -----------------------------
    # Relationships (FIXED)
    # -----------------------------
    product = relationship(
        "Product",
        back_populates="skus",
        lazy="joined"
    )

    tenant = relationship(
        "Tenant",
        back_populates="skus",
        lazy="joined"
    )

    competitor_prices = relationship(
        "CompetitorPrice",
        back_populates="sku",
        cascade="all, delete-orphan"
    )

    demand_signals = relationship(
        "DemandSignal",
        back_populates="sku",
        cascade="all, delete-orphan"
    )

    price_decisions = relationship(
        "PriceDecision",
        back_populates="sku",
        cascade="all, delete-orphan"
    )