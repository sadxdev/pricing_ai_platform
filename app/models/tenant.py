# app/models/tenant.py

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # relationships
    products = relationship("Product", back_populates="tenant")
    skus = relationship("SKU", back_populates="tenant")
    competitor_prices = relationship("CompetitorPrice", back_populates="tenant")
    demand_signals = relationship("DemandSignal", back_populates="tenant")

    skus = relationship(
        "SKU",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )

    demand_signals = relationship(
        "DemandSignal",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )