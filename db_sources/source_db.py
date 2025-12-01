import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Any, Mapping

from app_settings import AppSettings, get_app_settings


class SourceDatabase:

    def __init__(self, db_name: str, settings: AppSettings = get_app_settings()):
        self.name = db_name
        self.settings = settings
        self.db_config = settings.get_source_db_by_name(db_name)
        self.engine: Engine = self._create_engine()

    def _create_engine(self):
        if self.db_config is None:
            raise ValueError(
                f"Source database configuration for database '{self.name}' not found.")

        return create_engine(self.db_config.connection_string)

    def invoke_query(self, sql: str, params: Mapping[str, Any] | None = None) -> pd.DataFrame | None:

        results: pd.DataFrame | None = None

        if params is None:
            results = pd.read_sql_query(
                sql=text(sql),
                con=self.engine
            )
        else:
            results = pd.read_sql_query(
                sql=text(sql),
                con=self.engine,
                params=params
            )

        return results
