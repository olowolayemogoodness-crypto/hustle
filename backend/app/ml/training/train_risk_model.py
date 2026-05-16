from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from app.ml.utils.metrics import compute_classification_metrics


def save_model(model: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def train_risk_model(
    X,
    y,
    output_path: Path,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[LogisticRegression, dict[str, float]]:
    if X.shape[0] < 2:
        raise ValueError("At least two training rows are required.")

    if len(np.unique(y)) < 2:
        raise ValueError("Training labels require at least two classes.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        solver="liblinear",
        random_state=random_state,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = compute_classification_metrics(y_test, y_pred, y_prob)
    save_model(model, output_path)

    return model, metrics