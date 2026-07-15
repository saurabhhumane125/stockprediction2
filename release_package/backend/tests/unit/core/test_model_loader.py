from tests.fixtures.artifacts import get_artifacts


artifacts = get_artifacts()


def test_model_loaded():
    assert artifacts.model is not None


def test_scaler_loaded():
    assert artifacts.scaler is not None


def test_stock_encoder_loaded():
    assert artifacts.stock_encoder is not None


def test_metadata_loaded():
    assert artifacts.metadata is not None


def test_sequence_length():
    assert artifacts.sequence_length == 48


def test_feature_count():
    assert len(artifacts.features) == 20


def test_stock_classes():
    assert len(artifacts.stock_classes) == 10