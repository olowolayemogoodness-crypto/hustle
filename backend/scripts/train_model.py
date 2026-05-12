import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import logging

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")

# Load dataset
df = pd.read_csv(DATA_PATH)

# Features (inputs)
X = df[
    [
        "distance_km",
        "skill_overlap",
        "trust_score",
        "rating",
        "completion_rate",
        "disputes",
        "availability"
    ]
]

# Label (output)
y = df["label"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=6,
    random_state=42
    )

model.fit(X_train, y_train)

preds = model.predict(X_test)
accuracy = accuracy_score(y_test, preds)

print("Model Accuracy:", accuracy)

try:
    joblib.dump(model, MODEL_PATH)
    print("Model saved successfully")
except Exception as e:
    logging.error(f"Error occurred while saving the model: {e}")