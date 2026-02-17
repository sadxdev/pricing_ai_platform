import os
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from app.services.dataset_builder import DatasetBuilder


MODEL_DIR = "models"


class DemandModelService:

    # ----------------------------------------
    # Build model file path per tenant
    # ----------------------------------------
    @staticmethod
    def _get_model_path(tenant_id: int) -> str:
        os.makedirs(MODEL_DIR, exist_ok=True)
        return os.path.join(MODEL_DIR, f"demand_model_tenant_{tenant_id}.joblib")

    # ----------------------------------------
    # TRAIN MODEL (TENANT-AWARE)
    # ----------------------------------------
    @staticmethod
    async def train_model(db, tenant_id: int):

        dataset = await DatasetBuilder.build_training_dataset(db, tenant_id)

        if not dataset:
            raise ValueError("No data available for training")

        # -------- Prepare Data --------
        X = []
        y = []

        for row in dataset:
            X.append([
                float(row["avg_competitor_price"] or 0),
                float(row["min_competitor_price"] or 0),
                float(row["max_competitor_price"] or 0),
                float(row["views"] or 0),
                float(row["add_to_cart"] or 0)
            ])

            y.append(float(row["target_demand"] or 0))

        # -------- Train/Test Split --------
        if len(X) < 2:
            X_train, y_train = X, y
            X_test, y_test = X, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

        # -------- Train Model --------
        model = LinearRegression()
        model.fit(X_train, y_train)

        # -------- Evaluate --------
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)

        # -------- Save Model PER TENANT --------
        model_path = DemandModelService._get_model_path(tenant_id)
        joblib.dump(model, model_path)

        return {
            "status": "trained",
            "tenant_id": tenant_id,
            "mse": mse,
            "data_points": len(dataset),
            "model_path": model_path
        }

    # ----------------------------------------
    # LOAD MODEL (TENANT-AWARE)
    # ----------------------------------------
    @staticmethod
    def load_model(tenant_id: int):

        model_path = DemandModelService._get_model_path(tenant_id)

        if not os.path.exists(model_path):
            raise ValueError(f"Model not trained yet for tenant {tenant_id}")

        return joblib.load(model_path)

    # ----------------------------------------
    # PREDICT DEMAND (TENANT-AWARE)
    # ----------------------------------------
    @staticmethod
    def predict(tenant_id: int, features: dict):

        model = DemandModelService.load_model(tenant_id)

        X = [[
            float(features["avg_competitor_price"]),
            float(features["min_competitor_price"]),
            float(features["max_competitor_price"]),
            float(features["views"]),
            float(features["add_to_cart"])
        ]]

        prediction = model.predict(X)[0]

        return float(prediction)