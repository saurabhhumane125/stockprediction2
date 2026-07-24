from ml_engine.registry.manager import RegistryManager
from ml_engine.inference.engine import ProductionInferenceEngine

def check_legacy():
    rm = RegistryManager("ml_engine/model_registry")
    try:
        active = rm.get_active_model()
        print(f"Active model: {active['version']}")
        engine = ProductionInferenceEngine(rm)
        print("InferenceEngine initialized successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_legacy()
