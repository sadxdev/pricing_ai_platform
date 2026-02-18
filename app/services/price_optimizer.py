from typing import List, Dict
import numpy as np

from app.services.ml_model import DemandModelService


class PriceOptimizer:

    PRICE_STEPS = 20  # number of price points to simulate

    @staticmethod
    def _generate_price_range(
        base_price: float,
        min_price: float,
        max_price: float,
    ) -> List[float]:

        low = max(min_price, base_price * 0.7)
        high = max(max_price, base_price * 1.3)

        return list(np.linspace(low, high, PriceOptimizer.PRICE_STEPS))

    @staticmethod
    def optimize_price(
        *,
        tenant_id: int,
        cost_price: float,
        base_price: float,
        features: Dict,
        objective: str = "profit"  # "profit" or "revenue"
    ) -> Dict:

        prices = PriceOptimizer._generate_price_range(
            base_price=base_price,
            min_price=cost_price,
            max_price=features.get("max_competitor_price", base_price)
        )

        best_price = base_price
        best_metric = -1

        curve = []

        for price in prices:

            # clone features + inject simulated price
            sim_features = dict(features)
            sim_features["simulated_price"] = price

            predicted_demand = DemandModelService.predict(
                tenant_id,
                sim_features
            )

            revenue = price * predicted_demand
            profit = (price - cost_price) * predicted_demand

            metric = profit if objective == "profit" else revenue

            curve.append({
                "price": round(price, 2),
                "demand": round(predicted_demand, 2),
                "revenue": round(revenue, 2),
                "profit": round(profit, 2)
            })

            if metric > best_metric:
                best_metric = metric
                best_price = price

        return {
            "optimal_price": round(best_price, 2),
            "objective": objective,
            "expected_metric": round(best_metric, 2),
            "curve": curve
        }