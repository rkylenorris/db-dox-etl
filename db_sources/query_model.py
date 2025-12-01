from pathlib import Path
import pandas as pd
import sqlglot
import re

from .source_db import SourceDatabase
from app_settings import SqlType, get_app_settings

settings = get_app_settings()

QUERIES_PATH = Path('db_sources/queries')


class Query:

    def __init__(self, path: Path, source_db: SourceDatabase, base_dialect: SqlType = SqlType.SQLSERVER) -> None:
        self.name: str = path.stem[3:]
        self.file_name = path.name
        self.path: Path = path

    def _format_query_name(self, name: str) -> str:
        if bool(re.match(r"^[0-9]{2}_", name)):
            name = name[3:]
        return name.replace("_", " ").title()

    def _get_query_path(self, name: str):
        pass
