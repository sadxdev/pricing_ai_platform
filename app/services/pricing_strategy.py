class PricingStrategy:

    @staticmethod
    def apply_strategy(price: float, strategy: str) -> float:

        if strategy == "premium":
            return price * 1.10

        if strategy == "discount":
            return price * 0.95

        if strategy == "competitive":
            return price * 0.98

        return price