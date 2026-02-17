import os
import json
from datetime import datetime
from typing import Dict

MODEL_DIR = "models"


class MLMonitoringService:

    # ---------------------------------------
    # Metadata path per tenant
    # ---------------------------------------
    @staticmethod
    def _get_metadata_path(tenant_id: int) -> str:
        return os.path.join(MODEL_DIR, f"metadata_tenant_{tenant_id}.json")

    # ---------------------------------------
    # Read metadata
    # ---------------------------------------
    @staticmethod
    def load_metadata(tenant_id: int) -> Dict:
        path = MLMonitoringService._get_metadata_path(tenant_id)

        if not os.path.exists(path):
            raise ValueError("Model metadata not found. Train model first.")

        with open(path, "r") as f:
            return json.load(f)

    # ---------------------------------------
    # Model health calculation
    # ---------------------------------------
    @staticmethod
    def evaluate_model_health(tenant_id: int) -> Dict:

        metadata = MLMonitoringService.load_metadata(tenant_id)

        last_trained = datetime.fromisoformat(metadata["trained_at"])
        mse = metadata["mse"]
        data_points = metadata["data_points"]

        # ---------------------------
        # Calculate model age
        # ---------------------------
        age_days = (datetime.utcnow() - last_trained).days

        # ---------------------------
        # Basic drift simulation
        # (in real systems: use population drift)
        # ---------------------------
        drift_score = mse / (data_points + 1)

        # ---------------------------
        # Health classification
        # ---------------------------
        alerts = []

        status = "HEALTHY"

        if age_days > 7:
            alerts.append("MODEL_STALE")
            status = "WARNING"

        if mse > 100:
            alerts.append("HIGH_ERROR_RATE")
            status = "CRITICAL"

        if drift_score > 1:
            alerts.append("PREDICTION_DRIFT")
            status = "CRITICAL"

        return {
            "tenant_id": tenant_id,
            "model_status": status,
            "last_trained_at": metadata["trained_at"],
            "model_age_days": age_days,
            "mse": mse,
            "data_points": data_points,
            "drift_score": round(drift_score, 4),
            "alerts": alerts
        }