import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000"

def verify():
    print("="*50)
    print("VISION PIPELINE E2E VERIFICATION")
    print("="*50)
    
    # Create dummy image
    img_path = "test_vision.png"
    from PIL import Image
    Image.new('RGB', (800, 600), color='white').save(img_path)
    
    try:
        session = requests.Session()
        
        print("\n0. Logging in...")
        login_resp = session.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "password"})
        if login_resp.status_code != 200:
            print(f"FAILED: Login returned {login_resp.status_code}")
            return
        
        # Step 1: Upload
        print("\n1. Uploading Image...")
        with open(img_path, "rb") as f:
            resp = session.post(
                f"{BASE_URL}/api/v1/vision/upload", 
                files={"file": ("test_vision.png", f, "image/png")}
            )
        
        if resp.status_code != 200:
            print(f"FAILED: Upload returned {resp.status_code}")
            print(resp.text)
            return
            
        data = resp.json()
        filename = data["filename"]
        print(f"SUCCESS: Uploaded as {filename}")
        
        # Step 2: Predict
        print("\n2. Requesting Prediction Pipeline...")
        resp = session.post(
            f"{BASE_URL}/api/v1/vision/predict", 
            json={"filename": filename, "trace_id": "verify-123"}
        )
        
        if resp.status_code != 200:
            print(f"FAILED: Predict returned {resp.status_code}")
            print(resp.text)
            return
            
        result = resp.json()
        print("SUCCESS: Pipeline completed!")
        print("\n--- RESULTS ---")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Stock: {result['stock']}")
        print("\n--- TRACE ---")
        for k, v in result['trace'].items():
            print(f"{k}: {v}")
            
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    verify()
