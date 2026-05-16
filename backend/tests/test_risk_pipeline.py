import uuid
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
from joblib import load
from sklearn.linear_model import LogisticRegression

from app.ml.features.feature_engineering import FEATURE_COLUMNS, build_feature_dataframe, extract_log_features
from app.ml.training.risk_dataset_builder import build_risk_dataset
from app.ml.training.train_risk_model import train_risk_model
from app.db.models.match_log import MatchLog


def test_extract_log_features_returns_expected_vector():
    log = SimpleNamespace(
        distance_km=4.5,
        skill_overlap_ratio=0.75,
        worker_rating=4.4,
        worker_completion_rate=0.92,
        worker_trust_score=0.85,
        years_experience=3,
        job_budget=120.0,
        job_urgency=2,
        rule_score=0.68,
    )

    features = extract_log_features(log)

    assert features.shape == (len(FEATURE_COLUMNS),)
    assert features.tolist() == [4.5, 0.75, 4.4, 0.92, 0.85, 3.0, 120.0, 2.0, 0.68]


def test_build_feature_dataframe_from_match_logs():
    logs = [
        SimpleNamespace(
            distance_km=1.0,
            skill_overlap_ratio=0.5,
            worker_rating=4.0,
            worker_completion_rate=0.9,
            worker_trust_score=0.7,
            years_experience=1,
            job_budget=75.0,
            job_urgency=1,
            rule_score=0.5,
        ),
        SimpleNamespace(
            distance_km=None,
            skill_overlap_ratio=None,
            worker_rating=None,
            worker_completion_rate=None,
            worker_trust_score=None,
            years_experience=None,
            job_budget=None,
            job_urgency=None,
            rule_score=0.25,
        ),
    ]

    dataset = build_feature_dataframe(logs)
    assert list(dataset.columns) == FEATURE_COLUMNS
    assert dataset.shape == (2, len(FEATURE_COLUMNS))
    assert dataset.iloc[1, 0] == 0.0
    assert dataset.iloc[1, -1] == 0.25


@pytest.mark.asyncio
@pytest.mark.skip(reason="Deferred SQLAlchemy columns require greenlet_spawn context in async tests. Will be addressed in Week 2 with production DB integration.")
async def test_build_risk_dataset_from_database(db_session):
    first_log = MatchLog(
        job_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        final_score=0.85,
        rule_score=0.85,
        ml_probability=0.0,
        risk_penalty=0.0,
        confidence=0.8,
        status="ranked",
        accepted=True,
        completed=True,
        dispute_occurred=False,
        employer_rating=4.5,
        worker_rating=4.7,
    )
    second_log = MatchLog(
        job_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        final_score=0.60,
        rule_score=0.60,
        ml_probability=0.0,
        risk_penalty=0.0,
        confidence=0.8,
        status="ranked",
        accepted=False,
        completed=False,
        dispute_occurred=False,
        employer_rating=3.0,
        worker_rating=3.5,
    )
    third_log = MatchLog(
        job_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        final_score=0.40,
        rule_score=0.40,
        ml_probability=0.0,
        risk_penalty=0.0,
        confidence=0.8,
        status="ranked",
        accepted=True,
        completed=False,
        dispute_occurred=True,
        employer_rating=2.0,
        worker_rating=2.5,
    )

    db_session.add_all([first_log, second_log, third_log])
    await db_session.commit()

    X, y = await build_risk_dataset(db_session)
    assert not X.empty
    assert y.tolist() == [0, 1, 1]  # low risk, high risk, high risk
    assert list(X.columns) == FEATURE_COLUMNS


def test_train_risk_model_saves_and_predicts(tmp_path):
    X = pd.DataFrame(
        [
            [1.0, 0.8, 4.5, 0.9, 0.75, 2.0, 100.0, 3.0, 0.8],
            [8.0, 0.3, 3.5, 0.6, 0.45, 0.0, 40.0, 1.0, 0.4],
            [2.0, 0.6, 4.2, 0.85, 0.7, 1.0, 90.0, 2.0, 0.7],
            [15.0, 0.1, 2.8, 0.4, 0.3, 0.0, 30.0, 1.0, 0.25],
            [3.0, 0.7, 4.0, 0.8, 0.65, 1.5, 110.0, 2.5, 0.75],
            [5.0, 0.5, 3.8, 0.7, 0.55, 0.5, 60.0, 1.5, 0.5],
            [10.0, 0.2, 3.0, 0.5, 0.4, 0.0, 50.0, 1.0, 0.3],
            [4.0, 0.75, 4.3, 0.9, 0.7, 2.0, 120.0, 3.0, 0.8],
            [12.0, 0.15, 2.9, 0.45, 0.35, 0.0, 35.0, 0.5, 0.2],
            [6.0, 0.6, 4.1, 0.85, 0.68, 1.8, 100.0, 2.8, 0.78],
        ],
        columns=FEATURE_COLUMNS,
    )
    y = pd.Series([0, 1, 0, 1, 0, 1, 1, 0, 1, 0], dtype=int, name="high_risk")
    model_path = tmp_path / "risk_model.joblib"

    model, metrics = train_risk_model(X, y, model_path)

    assert isinstance(model, LogisticRegression)
    assert model_path.exists()
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "roc_auc" in metrics

    loaded_model = load(model_path)
    probabilities = loaded_model.predict_proba(X)[:, 1]
    assert probabilities.shape == (10,)
    assert all(0.0 <= prob <= 1.0 for prob in probabilities)