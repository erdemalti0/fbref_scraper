import json
import os
from sqlalchemy import MetaData, Table, Column, Integer, Text, DateTime, func, create_engine, inspect
from sqlalchemy.dialects.postgresql import JSONB, insert
from pydantic import BaseModel
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)


def _resolve_report_id(storage_dir: Path, report_id: str | None, fallback_prefix: str) -> str:
    if report_id:
        return report_id
    i = 1
    while (storage_dir / f"{fallback_prefix}{i}.json").exists():
        i += 1
    return f"{fallback_prefix}{i}"


def save_json(model, storage_dir: Path, report_id: str | None, fallback_prefix: str) -> Path | None:
    storage_dir.mkdir(parents=True, exist_ok=True)

    report_id = _resolve_report_id(storage_dir, report_id, fallback_prefix)

    path = storage_dir / f"{report_id}.json"
    path.write_text(
        json.dumps(model.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"Report saved: {path}")
    return path

def save_postgresql(connection_string: str, table_name: str, model: BaseModel, report_id: str) -> None:
    engine = create_engine(connection_string)

    table = Table(
        table_name,
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("report_id", Text, nullable=False, unique=True),
        Column("created_at", DateTime(timezone=True), server_default=func.now()),
        Column("data", JSONB, nullable=False),
    )

    insp = inspect(engine)
    if table_name not in insp.get_table_names():
        logger.info(f"Table {table_name} not found, creating")
        try:
            table.create(engine)
        except Exception as e:
            logger.exception(f"Table {table_name} could not be created: {e}")
            raise

        logger.info(f"Table {table_name} created")

    data = model.model_dump(mode="json")

    stmt = insert(table).values(report_id=report_id, data=data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["report_id"],
        set_={"data": stmt.excluded.data},
    )

    with engine.begin() as conn:
        conn.execute(stmt)

    logger.info(f"Report {report_id} saved to {table_name}")


def save(
    model: BaseModel,
    storage_dir: Path,
    report_id: str | None,
    fallback_prefix: str,
    table_name: str,
    storage_type: str = "json",
    connection_string: str | None = None,
) -> Path | None:
    """Save according to storage_type: 'json' | 'postgresql' | 'both'."""
    storage_type = (storage_type or "json").lower().strip()
    if storage_type not in ("json", "postgresql", "both"):
        raise ValueError(f"Unknown storage_type: {storage_type!r}")

    report_id = _resolve_report_id(storage_dir, report_id, fallback_prefix)
    path: Path | None = None

    if storage_type in ("json", "both"):
        path = save_json(model, storage_dir, report_id, fallback_prefix)

    if storage_type in ("postgresql", "both"):
        conn_str = connection_string or os.getenv("DB_CONNECTION_STRING")
        if not conn_str:
            logger.error("DB_CONNECTION_STRING is not set, skipping PostgreSQL save")
        else:
            save_postgresql(conn_str, table_name, model, report_id)

    return path