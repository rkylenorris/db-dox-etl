from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

from .utils import LogLevel, Environment, SqlType, CONNECTION_TEMPLATES, generate_run_guid


class DBCredentials(BaseModel):
    user: str
    password: str

    def __str__(self) -> str:
        return f"{self.user}:{self.password}"


class DbSettings(BaseModel):
    db_type: SqlType
    host: str  # server address
    port: int | None = None  # optional port
    database: str  # database name or file path for sqlite
    credentials: DBCredentials
    driver: str | None = None  # optional driver for some DBs

    @property
    def connection_string(self) -> str:
        if self.db_type == SqlType.SQLITE:
            template = CONNECTION_TEMPLATES["sqlite"]
            return template.format(
                path_to_file=self.database
            )
        elif self.db_type == SqlType.SQLSERVER:
            if self.port:
                template = CONNECTION_TEMPLATES["mssql"]["port"]
            else:
                template = CONNECTION_TEMPLATES["mssql"]["no_port"]
            return template.format(
                credentials=str(self.credentials),
                host=self.host,
                port=self.port if self.port else "",
                database=self.database,
                driver=self.driver if self.driver else "ODBC+Driver+17+for+SQL+Server"
            )
        else:
            template = CONNECTION_TEMPLATES.get(self.db_type.value)
            if template is None:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            return template.format(
                user=self.credentials.user,
                password=self.credentials.password,
                host=self.host,
                port=self.port if self.port else "",
                database=self.database
            )


class LogSettings(BaseModel):
    run_guid: str = generate_run_guid()
    console_log_level: LogLevel = LogLevel.INFO
    file_log_level: LogLevel = LogLevel.DEBUG
    log_directory: Path = Path("./logs")
    json_log: bool = True

    def __init__(self, **data):
        super().__init__(**data)
        self.log_directory.mkdir(parents=True, exist_ok=True)


class FeatureFlags(BaseModel):
    enable_llm_integration: bool = False


class AppSettings(BaseSettings):
    """Application settings for ETL process.
    Attributes:
        dox_db_settings (DbSettings): Database connection settings for documentation database.
        log_settings (LogSettings): Logging configuration settings.
        environment (Environment): Application environment (development, testing, production).
    """
    dox_db_settings: DbSettings
    source_dbs_settings: list[DbSettings]
    log_settings: LogSettings = LogSettings()
    feature_flags: FeatureFlags = FeatureFlags()
    environment: Environment = Environment.DEVELOPMENT

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
