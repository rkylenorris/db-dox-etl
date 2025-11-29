from dataclasses import dataclass
from uuid import uuid4
from pathlib import Path
import json

from .etl_log_context import LogLevel


def generate_etl_run_guid() -> str:
    """Generate a new ETL run GUID as a string.
    Returns:
        str: A new ETL run GUID.
    """
    return str(uuid4())


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

    def __init__(self, app_name: str, console_log_level: str, file_log_level: str,
                 log_directory: str, json_log: bool):
        self.app_name = app_name
        self.run_guid = generate_etl_run_guid()
        self.console_log_level = LogLevel(console_log_level)
        self.file_log_level = LogLevel(file_log_level)
        self.log_directory = Path(log_directory)
        self.json_log = json_log


def get_constants(path: Path) -> ETLLogConstants:
    """
    Load ETL logging constants from a JSON file.
    Args:
        path (Path): Path to the JSON file containing ETL logging constants.
    Returns:
        ETLLogConstants: The loaded ETL logging constants.
    """
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return ETLLogConstants(**data)


if __name__ == "__main__":
    # example usage
    constants_path = Path("etl_logging\\etl_log_constants.json")
    etl_logging_constants = get_constants(constants_path)
    print(etl_logging_constants)
