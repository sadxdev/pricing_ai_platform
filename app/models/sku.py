from sqlalchemy import String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SKU(Base):
    __tablename__ = "skus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Example: size / color variant
    variant: Mapped[str] = mapped_column(String(100), nullable=False)

    # Pricing fields
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2))
    base_price: Mapped[float] = mapped_column(Numeric(10, 2))

    # Relationship
    product = relationship("Product", backref="skus")