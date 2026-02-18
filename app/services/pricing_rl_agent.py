import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pricing_rl_state import PricingRLState
from app.models.price_decision import PriceDecision


class PricingRLAgent:

    # -----------------------------------------
    # Choose price (Explore vs Exploit)
    # -----------------------------------------
    @staticmethod
    async def choose_price(
        db: AsyncSession,
        tenant_id: int,
        sku_id: int,
        candidate_prices: list[float]
    ) -> float:

        result = await db.execute(
            select(PricingRLState).where(
                PricingRLState.tenant_id == tenant_id,
                PricingRLState.sku_id == sku_id
            )
        )

        state = result.scalar_one_or_none()

        # First time → create state
        if not state:
            state = PricingRLState(
                tenant_id=tenant_id,
                sku_id=sku_id,
                avg_reward=0.0,
                total_trials=0,
                epsilon=0.2
            )
            db.add(state)
            await db.commit()
            # Refresh to ensure we have the latest state object
            await db.refresh(state)

        # Exploration
        if random.random() < state.epsilon:
            return random.choice(candidate_prices)

        # Exploitation (choose best historical)
        result = await db.execute(
            select(PriceDecision)
            .where(
                PriceDecision.tenant_id == tenant_id,
                PriceDecision.sku_id == sku_id
            )
            .order_by(PriceDecision.recommended_price.desc())
            .limit(1)
        )

        best = result.scalar_one_or_none()

        if best:
            return float(best.recommended_price)

        return random.choice(candidate_prices)

    # -----------------------------------------
    # Update reward after outcome observed
    # -----------------------------------------
    @staticmethod
    async def update_reward(
        db: AsyncSession,
        tenant_id: int,
        sku_id: int,
        reward: float
    ):
        # Changed .scalar_one() to .scalar_one_or_none() to prevent 500 errors
        result = await db.execute(
            select(PricingRLState).where(
                PricingRLState.tenant_id == tenant_id,
                PricingRLState.sku_id == sku_id
            )
        )

        state = result.scalar_one_or_none()

        # Handle case where reward comes in for a SKU with no existing state
        if not state:
            state = PricingRLState(
                tenant_id=tenant_id,
                sku_id=sku_id,
                avg_reward=reward,
                total_trials=1,
                epsilon=0.2
            )
            db.add(state)
        else:
            # Update running average
            # Formula: new_avg = ((old_avg * count) + new_val) / (count + 1)
            total = state.total_trials
            state.avg_reward = ((state.avg_reward * total) + reward) / (total + 1)
            state.total_trials += 1

            # Slowly reduce exploration (Epsilon Decay)
            state.epsilon = max(0.05, state.epsilon * 0.99)

        await db.commit()