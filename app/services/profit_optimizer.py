class ProfitOptimizer:

    @staticmethod
    def calculate_profit(price: float, cost_price: float, demand: float) -> float:
        margin = price - cost_price
        return margin * demand

    @staticmethod
    def find_best_price(
        *,
        cost_price: float,
        predicted_demand: float,
        min_price: float,
        max_price: float
    ) -> dict:

        best_price = min_price
        best_profit = 0

        # Try 20 price points between min and max
        step = (max_price - min_price) / 20

        for i in range(21):
            price = min_price + (i * step)

            # simple demand elasticity assumption
            adjusted_demand = predicted_demand * (1 - (price - min_price) / max_price)

            profit = ProfitOptimizer.calculate_profit(price, cost_price, adjusted_demand)

            if profit > best_profit:
                best_profit = profit
                best_price = price

        return {
            "best_price": round(best_price, 2),
            "expected_profit": round(best_profit, 2)
        }