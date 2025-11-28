from enum import Enum
from uuid import uuid4


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
    "postgres": "postgresql+psycopg://{credentials}@{host}:{port}/{database}",
    "mysql": "mysql+mysqldb://{credentials}@{host}:{port}/{database}",
    "mysql+pymysql": "mysql+pymysql://{credentials}@{host}:{port}/{database}",
    "mssql":
        {
            "port": (
                "mssql+pyodbc://{credentials}@{host}:{port}/{database}"
                "?driver={driver}&TrustServerCertificate=yes"
            ),
            "no_port": (
                "mssql+pyodbc://{credentials}@{host}/{database}"
                "?driver={driver}&TrustServerCertificate=yes"
            )
        },
    "sqlite": "sqlite:///{path_to_file}"
}
