from enum import Enum


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
    SQLSERVER = "mssql"
    # ORACLE = "oracle"
    SQLITE = "sqlite"


CONNECTION_TEMPLATES = {
    "postgres": "postgresql+psycopg://{user}:{password}@{host}:{port}/{database}",
    "mysql": "mysql+mysqldb://{user}:{password}@{host}:{port}/{database}",
    "mysql+pymysql": "mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
    "mssql":
        {
            "port": (
                "mssql+pyodbc://{user}:{password}@{host}:{port}/{database}"
                "?driver={driver}&TrustServerCertificate=yes"
            ),
            "no_port": (
                "mssql+pyodbc://{user}:{password}@{host}/{database}"
                "?driver={driver}&TrustServerCertificate=yes"
            )
        },
    "sqlite": "sqlite:///{path_to_file}",
    "sqlite_memory": "sqlite:///:memory:",
}
