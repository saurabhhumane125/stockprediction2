import numpy as np

from app.core.model_loader import artifacts


class Preprocessor:

    def transform(self, stock: str, feature_rows):

        scaler = artifacts.scaler
        encoder = artifacts.stock_encoder

        if scaler is None:
            raise RuntimeError("Scaler not loaded.")

        if encoder is None:
            raise RuntimeError("Stock encoder not loaded.")

        feature_array = np.asarray(
            feature_rows,
            dtype=np.float32
        )

        if feature_array.shape != (48, 19):
            raise ValueError(
                "Expected feature shape (48, 19)"
            )

        try:
            stock_id = encoder.transform(
                [stock]
            )[0]

        except ValueError:
            raise ValueError(
                f"Unsupported stock: {stock}"
            )

        stock_column = np.full(
            (48, 1),
            stock_id,
            dtype=np.float32
        )

        feature_array = np.concatenate(
            [
                feature_array,
                stock_column
            ],
            axis=1
        )

        try:
            feature_array = scaler.transform(
                feature_array
            )
        except Exception as e:
            raise ValueError(
                f"Feature scaling failed: {e}"
            )

        feature_array = feature_array.reshape(
            1,
            48,
            20
        )

        return feature_array


preprocessor = Preprocessor()