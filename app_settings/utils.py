from dataclasses import dataclass
from enum import Enum
from uuid import uuid4
from functools import lru_cache

import sqlglot


@lru_cache
def generate_run_guid() -> str:
    """Generate a new ETL run GUID as a string.
    Returns:
        str: A new ETL run GUID.
    """
    return str(uuid4())


class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogLevel(Enum):
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SqlType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MYSQL_PYMYSQL = "mysql+pymysql"
    SQLSERVER = "mssql"
    # ORACLE = "oracle"
    SQLITE = "sqlite"


CONNECTION_TEMPLATES = {
    "postgresql": "postgresql+psycopg://{credentials}@{host}:{port}/{database}",
    "mysql": "mysql+mysqldb://{credentials}@{host}:{port}/{database}",
    "mysql+pymysql": "mysql+pymysql://{credentials}@{host}:{port}/{database}",
    "mssql":
        {
            "port": (
                "mssql+pyodbc://{credentials}@{host}:{port}/{database}"
                "?driver={driver}&TrustServerCertificate=yes&Encrypt=no"
            ),
            "no_port": (
                "mssql+pyodbc://{credentials}@{host}/{database}"
                "?driver={driver}&TrustServerCertificate=yes&Encrypt=no"
            )
        },
    "sqlite": "sqlite:///{path_to_file}"
}


@dataclass(frozen=True)
class SqlGlotDialectRegistry:
    mapping: dict[SqlType, sqlglot.Dialect]

    def __init__(self):
        for sql_type in SqlType:
            dialect = self._derive_dialect_from_sql_type(sql_type)
            if dialect is None:
                raise ValueError(
                    f"Corresponding sqlglot dialect not found for sql type {sql_type!r}"
                )
            self.mapping[sql_type] = dialect

    def _derive_dialect_from_sql_type(self, sql_type: SqlType) -> sqlglot.Dialect | None:
        type_name = sql_type.value

        if type_name == 'mssql':
            d = sqlglot.Dialect.get('tsql')
            if d:
                return d()
        elif "+" in type_name:
            d = sqlglot.Dialect.get(type_name.split('+')[0])
            if d:
                return d()
        elif "postgres" in type_name:
            d = sqlglot.Dialect.get('postgres')
            if d:
                return d()
        else:
            d = sqlglot.Dialect.get(type_name)
            if d:
                return d()

        return None

    def get(self, sql_type: SqlType) -> sqlglot.Dialect:
        """Return the sqlglot dialect object for the given SQL type."""
        try:
            return self.mapping[sql_type]
        except KeyError:
            raise ValueError(f"No sqlglot dialect registered for {sql_type!r}")
