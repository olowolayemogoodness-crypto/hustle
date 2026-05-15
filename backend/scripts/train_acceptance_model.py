from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if os.getenv("DATABASE_URL") and not os.getenv("HUSTLE_DATABASE_URL"):
    os.environ["HUSTLE_DATABASE_URL"] = os.getenv("DATABASE_URL")

from app.db.session import AsyncSessionLocal
from app.ml.training.dataset_builder import build_dataset
from app.ml.training.train_acceptance_model import train_acceptance_model
from app.core.config import settings


def get_model_path() -> Path:
    return ROOT_DIR / "app" / "ml" / "models" / "acceptance_model.joblib"


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
        X, y = await build_dataset(session)

    output_path = get_model_path()
    model, metrics = train_acceptance_model(X, y, output_path)

    print("Model training complete")
    print(f"Model saved to: {output_path}")
    print("Evaluation metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")


if __name__ == "__main__":
    asyncio.run(run_training())
