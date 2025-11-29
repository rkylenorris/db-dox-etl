from dataclasses import dataclass
from pathlib import Path
from app_settings import get_app_settings, AppSettings, LogLevel


DEFAULT_EXTRA_FIELDS = [
    "app_name",
    "source_db_name",
    "etl_run_guid",
    "etl_run_id",
    "etl_phase",
    "etl_step"
]

settings = get_app_settings()


@dataclass
class ETLLogConstants:
    """Constants for ETL logging configuration.
    Attributes:
        app_name (str): Name of the application.
        run_guid (str): Unique identifier for the ETL run.
        console_log_level (LogLevel): Log level for console output.
        file_log_level (LogLevel): Log level for file output.
        log_directory (Path): Directory path for log files.
        json_log (bool): Whether to output logs in JSON format.
    """
    app_name: str
    run_guid: str
    console_log_level: LogLevel
    file_log_level: LogLevel
    log_directory: Path
    json_log: bool

    def __init__(self, settings: AppSettings):
        self.app_name = settings.app_name
        self.run_guid = settings.log.run_guid
        self.console_log_level = settings.log.console_log_level
        self.file_log_level = settings.log.file_log_level
        self.log_directory = settings.log.log_directory
        self.json_log = settings.log.json_log


def get_constants() -> ETLLogConstants:
    """Load ETL logging constants from application settings."""
    return ETLLogConstants(settings)


if __name__ == "__main__":
    # example usage
    etl_logging_constants = get_constants()
    print(etl_logging_constants)
