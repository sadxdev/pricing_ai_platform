from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base_class import Base


class DemandSignal(Base):
    __tablename__ = "demand_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # -----------------------------
    # Tenant
    # -----------------------------
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # -----------------------------
    # SKU RELATION (THIS WAS MISSING)
    # -----------------------------
    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # -----------------------------
    # Signal Data
    # -----------------------------
    signal_type: Mapped[str] = mapped_column(String(50), index=True)
    value: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    # -----------------------------
    # Relationships
    # -----------------------------
    sku = relationship("SKU", back_populates="demand_signals")
    tenant = relationship("Tenant", back_populates="demand_signals")