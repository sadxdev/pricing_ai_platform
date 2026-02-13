from sqlalchemy import Integer, ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


class PriceDecision(Base):
    __tablename__ = "price_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id", ondelete="CASCADE"),
        index=True
    )

    recommended_price: Mapped[float] = mapped_column(Numeric(10, 2))

    strategy: Mapped[str] = mapped_column(String(100))  # e.g. undercut, match, premium
    reason: Mapped[str] = mapped_column(String(255))

    model_version: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    sku = relationship("SKU", backref="price_decisions")