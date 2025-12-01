from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel, model_validator, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .utils import LogLevel, Environment, SqlType, CONNECTION_TEMPLATES, generate_run_guid, SqlGlotDialectRegistry


class DBCredentials(BaseModel):
    """
    Database credentials model.
    Attributes:
        user (str): Username for database authentication.
        password (str): Password for database authentication.
    """
    user: str
    password: str

    def __str__(self) -> str:
        return f"{self.user}:{self.password}"


class DbSettings(BaseModel):
    """
    Database connection settings model.
    Attributes:
         db_type (SqlType): Type of the database (e.g., SQLITE, POSTGRES, MYSQL, SQLSERVER).
        host (str): Server address.
        port (int | None): Optional port number.
        database (str): Database name or file path for sqlite.
        credentials (DBCredentials): Database credentials.
        driver (str | None): Optional driver for some databases.
    """
    db_type: SqlType
    host: str  # server address
    port: int | None = None  # optional port
    database: str  # database name or file path for sqlite
    credentials: DBCredentials
    driver: str | None = None  # optional driver for some DBs

    @property
    def connection_string(self) -> str:
        """
        Generates the database connection string based on the settings.
        Returns:
            str: Formatted connection string.
        """
        if self.db_type == SqlType.SQLITE:
            template = CONNECTION_TEMPLATES["sqlite"]
            return template.format(
                path_to_file=self.database
            )
        elif self.db_type == SqlType.SQLSERVER:
            if self.port:
                template = CONNECTION_TEMPLATES["mssql"]["port"]
                return template.format(
                    credentials=str(self.credentials),
                    host=self.host,
                    port=self.port if self.port else "",
                    database=self.database,
                    driver=self.driver if self.driver else "ODBC+Driver+17+for+SQL+Server"
                )
            else:
                template = CONNECTION_TEMPLATES["mssql"]["no_port"]
                return template.format(
                    credentials=str(self.credentials),
                    host=self.host,
                    database=self.database,
                    driver=self.driver if self.driver else "ODBC+Driver+17+for+SQL+Server"
                )
        else:
            template = CONNECTION_TEMPLATES.get(self.db_type.value)
            if template is None:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            return template.format(
                credentials=str(self.credentials),
                host=self.host,
                port=self.port if self.port else "",
                database=self.database
            )


class LogSettings(BaseModel):
    """Logging configuration settings.
    Attributes:
        run_guid (str): Unique identifier for the log run.
        console_log_level (LogLevel): Log level for console output.
        file_log_level (LogLevel): Log level for file output.
        log_directory (Path): Directory to store log files.
        json_log (bool): Whether to log in JSON format.
    """
    # run_guid: str = generate_run_guid()
    console_log_level: LogLevel = LogLevel.INFO
    file_log_level: LogLevel = LogLevel.DEBUG
    log_directory: Path = Path("./logs")
    json_log: bool = True
    run_guid: str = PrivateAttr(default_factory=generate_run_guid)

    def __init__(self, **data):
        super().__init__(**data)
        # create log directory if it doesn't exist
        self.log_directory.mkdir(parents=True, exist_ok=True)


class FeatureFlags(BaseModel):
    """Feature flags for enabling/disabling features."""
    enable_llm_integration: bool = False


class AppSettings(BaseSettings):
    """Application settings for db-dox ETL process.
    Attributes:
        app_name (str): Name of the application.
        dox_db (DbSettings | None): Settings for the documentation database.
        source_dbs_file (str | None): Path to JSON file with source database settings.
        source_dbs (list[DbSettings]): List of source database settings.
        log (LogSettings): Logging configuration settings.
        feature_flags (FeatureFlags): Feature flags for enabling/disabling features.
        environment (Environment): Application environment (development, staging, production).

    """
    app_name: str = "db-dox ETL"
    dox_db: DbSettings | None = None
    source_dbs_file: str | None = None
    source_dbs: list[DbSettings] = []
    log: LogSettings = LogSettings()
    feature_flags: FeatureFlags = FeatureFlags()
    environment: Environment = Environment.DEVELOPMENT
    sql_glot_dialect_registry: SqlGlotDialectRegistry = PrivateAttr(
        default_factory=SqlGlotDialectRegistry
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__"
    )

    @model_validator(mode="after")
    def load_source_dbs(self):
        """
        If source_dbs_file is set, load JSON and parse as list[DbSettings].
        """
        if self.source_dbs_file:
            import json
            from pathlib import Path

            path = Path(self.source_dbs_file)
            if not path.exists():
                raise FileNotFoundError(
                    f"Source DB settings file not found: {path}"
                )

            raw = json.loads(path.read_text())
            # trigger Pydantic validation
            self.source_dbs = [DbSettings.model_validate(item) for item in raw]

        return self

    def get_source_db_by_name(self, name: str) -> DbSettings | None:
        """Get source database settings by database name.
        Args:
            name (str): Database name to search for.
        Returns:
            DbSettings | None: Matching DbSettings instance or None if not found.
        """
        for db_settings in self.source_dbs:
            if db_settings.database == name:
                return db_settings
        return None


@lru_cache
def get_app_settings() -> AppSettings:
    """Get cached application settings instance.
    Returns:
        AppSettings: Application settings instance.
    """
    return AppSettings()


if __name__ == "__main__":
    # print(app_settings)
    from dotenv import dotenv_values

    print("---- Raw .env contents as python-dotenv sees them ----")
    print(dotenv_values(".env"))

    print("\n---- What AppSettings actually sees ----")
    settings = AppSettings()
    print(settings.model_dump())
