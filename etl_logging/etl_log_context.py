from enum import StrEnum
from typing import Optional
from dataclasses import dataclass, asdict

from .etl_step import step_to_str, EtlStepType, get_phase_from_step


class LogLevel(StrEnum):
    """Standard log levels for configuration."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ETLLogContext:
    """
    Contextual information for ETL logging.
    Attributes:
        source_db_name (str): Name of the source database.
        etl_run_guid (str): Unique identifier for the ETL run.
        etl_phase (str): Current ETL phase (e.g. 'extract', 'parse', 'transform', 'load').
        etl_step (str): Current ETL step identifier.

    Methods:
        update_step(etl_step: EtlStepType) -> None:
            Update the current ETL step and phase.
        update_source_db_name(source_db_name: str) -> None:
            Update the source database name.
        to_bind_kwargs() -> dict:
            Convert the context to a dictionary for logger binding.
    """
    source_db_name: str
    etl_run_guid: str
    etl_phase: str
    etl_step: str

    def __init__(self, source_db_name: Optional[str] = None,
                 etl_run_guid: Optional[str] = None, etl_step: Optional[EtlStepType] = None):
        self.source_db_name = source_db_name if source_db_name is not None else "-"
        self.etl_run_guid = etl_run_guid if etl_run_guid is not None else "-"
        self.etl_step = step_to_str(etl_step) if etl_step is not None else "-"
        self.etl_phase = get_phase_from_step(
            etl_step) if etl_step is not None else "-"

    def update_step(self, etl_step: EtlStepType) -> None:
        self.etl_step = step_to_str(etl_step)
        self.etl_phase = get_phase_from_step(etl_step)

    def update_source_db_name(self, source_db_name: str) -> None:
        self.source_db_name = source_db_name

    def to_bind_kwargs(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
