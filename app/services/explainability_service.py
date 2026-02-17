import shap
import numpy as np

from app.services.ml_model import DemandModelService


class ExplainabilityService:

    FEATURE_ORDER = [
        "avg_competitor_price",
        "min_competitor_price",
        "max_competitor_price",
        "views",
        "add_to_cart"
    ]

    @staticmethod
    def explain_demand(tenant_id: int, features: dict):

        # Load trained model
        model = DemandModelService.load_model(tenant_id)

        # Convert features to array
        X = np.array([[
            float(features["avg_competitor_price"]),
            float(features["min_competitor_price"]),
            float(features["max_competitor_price"]),
            float(features["views"]),
            float(features["add_to_cart"]),
        ]])

        # SHAP explainer
        explainer = shap.Explainer(model, X)

        shap_values = explainer(X)

        contributions = shap_values.values[0]

        # Map feature → contribution
        feature_contributions = {
            feature: float(contributions[i])
            for i, feature in enumerate(ExplainabilityService.FEATURE_ORDER)
        }

        prediction = float(model.predict(X)[0])

        return {
            "predicted_demand": prediction,
            "feature_contributions": feature_contributions
        }