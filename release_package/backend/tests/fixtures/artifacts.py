from app.core.model_loader import artifacts


def get_artifacts():

    if artifacts.model is None:
        artifacts.load_artifacts()

    return artifacts