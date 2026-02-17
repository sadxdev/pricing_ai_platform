from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id"),
        index=True
    )

    # relationship
    tenant = relationship("Tenant", back_populates="products")

    skus = relationship(
        "SKU",
        back_populates="product",
        cascade="all, delete-orphan"
    )