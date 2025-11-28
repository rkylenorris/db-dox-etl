from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils import LogLevel, Environment, SqlType, CONNECTION_TEMPLATES, generate_run_guid


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
        app_name (str): Name of the application.
        source_dbs_file (str | None): Path to JSON file with source database settings.
        log_settings (LogSettings): Logging configuration settings.
        feature_flags (FeatureFlags): Feature flags for enabling/disabling features.
        environment (Environment): Application environment (development, testing, production).
    """
    app_name: str = "db_dox_etl"
    dox_db: DbSettings | None = None
    source_dbs_file: str | None = None
    source_dbs: list[DbSettings] = []
    log: LogSettings = LogSettings()
    feature_flags: FeatureFlags = FeatureFlags()
    environment: Environment = Environment.DEVELOPMENT

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__"
    )

    @model_validator(mode="after")
    def load_source_dbs(self):
        """
        If SOURCE_DBS_FILE is set, load JSON and parse as list[DbSettings].
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
            self.source_dbs = [
                DbSettings.model_validate(item) for item in raw]

        return self


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


if __name__ == "__main__":
    # print(app_settings)
    from dotenv import dotenv_values

    print("---- Raw .env contents as python-dotenv sees them ----")
    print(dotenv_values(".env"))

    print("\n---- What AppSettings actually sees ----")
    settings = AppSettings()
    print(settings.model_dump())
