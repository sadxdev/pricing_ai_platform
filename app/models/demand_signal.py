from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base


class DemandSignal(Base):
    __tablename__ = "demand_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id", ondelete="CASCADE"),
        index=True
    )

    signal_type: Mapped[str] = mapped_column(String(50), index=True)
    value: Mapped[int] = mapped_column(Integer)

    captured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    sku = relationship("SKU", backref="demand_signals")