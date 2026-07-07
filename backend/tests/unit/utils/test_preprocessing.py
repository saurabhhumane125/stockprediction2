import pytest

from tests.fixtures.artifacts import get_artifacts
from app.utils.preprocessing import preprocessor


get_artifacts()


def test_invalid_sequence_length():

    with pytest.raises(
        ValueError,
        match="Expected feature shape",
    ):

        preprocessor.transform(
            "RELIANCE",
            [[1.0] * 19],
        )


def test_invalid_stock():

    features = [
        [1.0] * 19
        for _ in range(48)
    ]

    with pytest.raises(
        ValueError,
        match="Unsupported stock",
    ):

        preprocessor.transform(
            "INVALID_STOCK",
            features,
        )


def test_valid_preprocessing():

    features = [
        [1.0] * 19
        for _ in range(48)
    ]

    output = preprocessor.transform(
        "RELIANCE",
        features,
    )

    assert output.shape == (
        1,
        48,
        20,
    )