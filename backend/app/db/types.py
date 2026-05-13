import uuid

from sqlalchemy import CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL UUID type on Postgres. Falls back to CHAR(36) on other
    databases (including SQLite).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, uuid.UUID):
            return str(value)

        if isinstance(value, int):
            return str(uuid.UUID(int=value))

        if isinstance(value, str):
            try:
                return str(uuid.UUID(value))
            except ValueError:
                if value.isdigit():
                    return str(uuid.UUID(int=int(value)))
                raise

        raise TypeError(f"Invalid UUID value: {value!r}")

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, uuid.UUID):
            return value

        return uuid.UUID(value)
