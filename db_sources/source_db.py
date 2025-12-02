from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Any, Mapping

from app_settings import AppSettings, get_app_settings
from .query_model import Query


class SourceDatabase:

    def __init__(self, db_name: str, settings: AppSettings = get_app_settings()):
        self.name = db_name
        self.settings = settings
        self.db_config = settings.get_source_db_by_name(db_name)
        self.engine: Engine = self._create_engine()

    def _create_engine(self) -> Engine:
        if self.db_config is None:
            raise ValueError(
                f"Source database configuration for database '{self.name}' not found.")

        return create_engine(self.db_config.connection_string)

    def stream_query(self, sql_query: Query, params: Mapping[str, Any] | None = None, chunk_size: int = 5_000):

        with self.engine.connect() as conn:
            cursor = conn.execution_options(stream_results=True).exec_driver_sql(
                sql_query.sql_text,
                params or {}
            )

            while True:
                rows = cursor.fetchmany(chunk_size)
                if not rows:
                    break
                yield rows
