from pathlib import Path
import json
import joblib

from tensorflow.keras.models import load_model


class ModelArtifacts:
    """
    Loads and stores all ML deployment artifacts.

    This class is initialized once during application startup
    and reused for all prediction requests.
    """

    def __init__(self):

        project_root = Path(__file__).resolve().parents[3]

        self.models_dir = project_root / "models"

        self.model = None
        self.scaler = None
        self.stock_encoder = None
        self.metadata = None

    def _verify_files(self):

        required_files = [
            "gru_v1.keras",
            "feature_scaler.pkl",
            "stock_encoder.pkl",
            "model_metadata.json",
        ]

        missing = []

        for file in required_files:

            path = self.models_dir / file

            if not path.exists():
                missing.append(file)

        if missing:
            raise FileNotFoundError(
                f"Missing model artifacts: {missing}"
            )

    def load_artifacts(self):

        self._verify_files()

        self.model = load_model(
            self.models_dir / "gru_v1.keras",
            compile=False,

        )

        self.scaler = joblib.load(
            self.models_dir / "feature_scaler.pkl"
        )

        self.stock_encoder = joblib.load(
            self.models_dir / "stock_encoder.pkl"
        )

        with open(
            self.models_dir / "model_metadata.json",
            "r",
            encoding="utf-8",
        ) as f:

            self.metadata = json.load(f)

        return self

    @property
    def features(self):
        return self.metadata["features"]

    @property
    def sequence_length(self):
        return self.metadata["sequence_length"]

    @property
    def stock_classes(self):
        return self.metadata["stock_classes"]


artifacts = ModelArtifacts()