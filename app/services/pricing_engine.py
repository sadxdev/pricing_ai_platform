class PricingEngine:

    MIN_MARGIN_PERCENT = 10  # minimum 10% margin
    UNDERCUT_PERCENT = 2     # 2% cheaper than competitor
    DEMAND_INCREASE_PERCENT = 5
    DEMAND_DECREASE_PERCENT = 5

    @staticmethod
    def calculate_price(
        *,
        cost_price: float,
        base_price: float,
        predicted_demand: float,
        avg_comp_price: float,
        min_comp_price: float,
        max_comp_price: float,
    ) -> dict:

        # ---- Minimum allowed price (cost + margin) ----
        min_allowed_price = cost_price * (1 + PricingEngine.MIN_MARGIN_PERCENT / 100)

        # ---- Start with base price ----
        price = base_price

        # ---- Demand based adjustment ----
        if predicted_demand > 20:
            price *= (1 + PricingEngine.DEMAND_INCREASE_PERCENT / 100)

        elif predicted_demand < 5:
            price *= (1 - PricingEngine.DEMAND_DECREASE_PERCENT / 100)

        # ---- Competitor adjustment ----
        if min_comp_price > 0:
            target_price = min_comp_price * (1 - PricingEngine.UNDERCUT_PERCENT / 100)

            # choose lower between our calculated price and competitor undercut
            price = min(price, target_price)

        # ---- Ensure not below cost margin ----
        final_price = max(price, min_allowed_price)

        return {
            "recommended_price": round(final_price, 2),
            "min_allowed_price": round(min_allowed_price, 2),
            "strategy": {
                "demand_signal": predicted_demand,
                "competitor_anchor": min_comp_price,
            }
        }