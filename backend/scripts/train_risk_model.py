from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if os.getenv("DATABASE_URL") and not os.getenv("HUSTLE_DATABASE_URL"):
    os.environ["HUSTLE_DATABASE_URL"] = os.getenv("DATABASE_URL")

from app.db.session import AsyncSessionLocal
from app.ml.training.risk_dataset_builder import build_risk_dataset
from app.ml.training.train_risk_model import train_risk_model
from app.ml.calibration import PlattScaler
from app.core.config import settings


def get_model_path() -> Path:
    return ROOT_DIR / "app" / "ml" / "models" / "risk_model.joblib"


def get_calibration_path() -> Path:
    return ROOT_DIR / "app" / "ml" / "models" / "risk_calibration.joblib"


def validate_database_url() -> None:
    database_url = os.getenv("HUSTLE_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError(
            "DATABASE_URL or HUSTLE_DATABASE_URL must be set for training."
        )
    if database_url.startswith("sqlite"):
        raise EnvironmentError(
            "Training must run against PostgreSQL via DATABASE_URL, not SQLite."
        )


async def run_training() -> None:
    validate_database_url()

    async with AsyncSessionLocal() as session:
        X, y = await build_risk_dataset(session)

    # Split into train/test first
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # Further split test into validation and calibration
    X_val, X_calib, y_val, y_calib = train_test_split(
        X_test,
        y_test,
        test_size=0.5,
        random_state=42,
        stratify=y_test,
    )

    # Train main model on train split
    output_path = get_model_path()
    model, metrics = train_risk_model(
        X_train, y_train, output_path, test_size=0.0, random_state=42
    )

    print("Risk model training complete")
    print(f"Model saved to: {output_path}")
    print("Evaluation metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

    # Fit calibration on validation set
    print("\nFitting calibration scaler...")
    y_proba_val = model.predict_proba(X_val)[:, 1]
    
    scaler = PlattScaler()
    scaler.fit(y_proba_val, y_val)
    
    calibration_path = get_calibration_path()
    scaler.save(calibration_path)
    print(f"Calibration saved to: {calibration_path}")

    # Verify on calibration set
    y_proba_calib = model.predict_proba(X_calib)[:, 1]
    y_proba_calib_scaled = scaler.calibrate(y_proba_calib)
    print(f"\nCalibration verification (on calibration set):")
    print(f"  Raw probabilities: mean={y_proba_calib.mean():.4f}, std={y_proba_calib.std():.4f}")
    print(f"  Calibrated probabilities: mean={y_proba_calib_scaled.mean():.4f}, std={y_proba_calib_scaled.std():.4f}")


if __name__ == "__main__":
    asyncio.run(run_training())