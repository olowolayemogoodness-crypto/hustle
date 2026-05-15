from typing import Tuple

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.match_log import MatchLog
from app.ml.features.feature_engineering import FEATURE_COLUMNS, build_feature_dataframe


async def load_match_logs(session: AsyncSession) -> list[MatchLog]:
    stmt = select(MatchLog)
    result = await session.execute(stmt)
    return result.scalars().all()


def build_successful_match_labels(match_logs: list[MatchLog]) -> pd.Series:
    labels = [
        int(bool(log.accepted) and bool(log.completed) and not bool(log.dispute_occurred))
        for log in match_logs
    ]
    return pd.Series(labels, dtype=int, name="successful_match")


async def build_dataset(session: AsyncSession) -> tuple[pd.DataFrame, pd.Series]:
    match_logs = await load_match_logs(session)
    if not match_logs:
        raise ValueError("No match log records available for training.")

    dataset = build_feature_dataframe(match_logs)
    labels = build_successful_match_labels(match_logs)

    if dataset.empty or labels.empty:
        raise ValueError("Dataset generation produced no rows.")

    return dataset, labels
