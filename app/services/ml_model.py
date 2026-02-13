import os
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from app.services.dataset_builder import DatasetBuilder


MODEL_PATH = "models/demand_model.joblib"


class DemandModelService:

    @staticmethod
    async def train_model(db):

        dataset = await DatasetBuilder.build_training_dataset(db)

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

            y.append(row["target_demand"])

        # -------- Train/Test Split --------
        if len(X) < 2:
            # Not enough data for split → train on full dataset
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

        # -------- Save Model --------
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, MODEL_PATH)

        return {
            "status": "trained",
            "mse": mse,
            "data_points": len(dataset)
        }

    @staticmethod
    def load_model():
        if not os.path.exists(MODEL_PATH):
            raise ValueError("Model not trained yet")

        return joblib.load(MODEL_PATH)

    @staticmethod
    def predict(features: dict):

        model = DemandModelService.load_model()

        X = [[
            features["avg_competitor_price"],
            features["min_competitor_price"],
            features["max_competitor_price"],
            features["views"],
            features["add_to_cart"]
        ]]

        prediction = model.predict(X)[0]

        return float(prediction)