from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class PricingRLState(Base):
    __tablename__ = "pricing_rl_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        index=True
    )

    sku_id: Mapped[int] = mapped_column(
        ForeignKey("skus.id", ondelete="CASCADE"),
        index=True
    )

    # Learned metrics
    avg_reward: Mapped[float] = mapped_column(Float, default=0.0)
    total_trials: Mapped[int] = mapped_column(Integer, default=0)

    # Exploration factor
    epsilon: Mapped[float] = mapped_column(Float, default=0.1)

    sku = relationship("SKU")