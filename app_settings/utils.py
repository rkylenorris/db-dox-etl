from dataclasses import dataclass, field
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
    mapping: dict[SqlType, type[sqlglot.Dialect]] = field(
        default_factory=dict, init=False
    )

    def __post_init__(self) -> None:
        m: dict[SqlType, type[sqlglot.Dialect]] = {}

        for sql_type in SqlType:
            dialect_class = self._derive_dialect_from_sql_type(sql_type)
            if dialect_class is None:
                raise ValueError(
                    f"Corresponding sqlglot dialect class not found for sql type {sql_type!r}"
                )
            m[sql_type] = dialect_class

    def _derive_dialect_from_sql_type(self, sql_type: SqlType) -> type[sqlglot.Dialect] | None:
        type_name = sql_type.value

        dialect_class: type[sqlglot.Dialect] | None = None

        if type_name == 'mssql':
            dialect_class = sqlglot.Dialect.get('tsql')

        elif "+" in type_name:
            dialect_class = sqlglot.Dialect.get(type_name.split('+')[0])

        elif "postgres" in type_name:
            dialect_class = sqlglot.Dialect.get('postgres')

        else:
            dialect_class = sqlglot.Dialect.get(type_name)

        return dialect_class

    def get(self, sql_type: SqlType) -> sqlglot.Dialect:
        """Return the sqlglot dialect object for the given SQL type."""
        try:
            return self.mapping[sql_type]()
        except KeyError:
            raise ValueError(f"No sqlglot dialect registered for {sql_type!r}")
