import os
import joblib

# Configure file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../../scripts/model.joblib")

model = joblib.load(MODEL_PATH)

def predict_success(features : dict) -> float:
    X = [list(features.values())]
    prob = model.predict_proba(X)[0][1]
    return float(prob)

