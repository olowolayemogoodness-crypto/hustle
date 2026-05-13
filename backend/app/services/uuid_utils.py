import re
import uuid
from typing import Any
from uuid import UUID

UUID_PAIR_RE = re.compile(
    r"^(?P<job>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})-(?P<worker>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"
)


def parse_uuid(value: Any) -> UUID:
    """Safely parse a UUID from strings, ints, or UUID objects.

    Supports legacy numeric IDs by interpreting integer values as
    low-order UUID integers.
    """
    if isinstance(value, UUID):
        return value

    if isinstance(value, uuid.UUID):
        return value

    if isinstance(value, int):
        return UUID(int=value)

    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            if value.isdigit():
                return UUID(int=int(value))
            raise

    raise TypeError(f"Invalid UUID value: {value!r}")


def split_match_log_id(match_log_id: str) -> tuple[str, str]:
    """Parse a combined match log identifier.

    Supports both legacy integer pairs like `1-102` and UUID pairs that
    may themselves contain hyphens.
    """
    if ":" in match_log_id:
        job_id, worker_id = match_log_id.split(":", 1)
        return job_id, worker_id

    match = UUID_PAIR_RE.fullmatch(match_log_id)
    if match:
        return match.group("job"), match.group("worker")

    if "-" in match_log_id:
        return match_log_id.split("-", 1)

    raise ValueError(f"Invalid match_log_id format: {match_log_id}")
