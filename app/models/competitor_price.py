from sqlalchemy import Integer, ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


class CompetitorPrice(Base):
    __tablename__ = "competitor_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id", ondelete="CASCADE"),
        index=True
    )

    competitor_name: Mapped[str] = mapped_column(String(255), nullable=False)

    competitor_price: Mapped[float] = mapped_column(Numeric(10, 2))

    captured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    sku = relationship("SKU", backref="competitor_prices")