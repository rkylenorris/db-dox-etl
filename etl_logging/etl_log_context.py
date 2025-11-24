from uuid import uuid4
from enum import StrEnum
from typing import Optional
from dataclasses import dataclass, asdict

from .etl_step import step_to_str, EtlStepType, get_phase_from_step


def generate_etl_run_guid() -> str:
    """Generate a new ETL run GUID as a string."""
    return str(uuid4())


# constant for run guid
ETL_RUN_GUID = generate_etl_run_guid()


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
    source_db_name: str
    etl_run_id: str
    etl_phase: str
    etl_step: str

    def __init__(self, source_db_name: Optional[str] = None,
                 etl_run_id: Optional[str] = None, etl_step: Optional[EtlStepType] = None):
        self.source_db_name = source_db_name if source_db_name is not None else "-"
        self.etl_run_id = etl_run_id if etl_run_id is not None else "-"
        self.etl_step = step_to_str(etl_step) if etl_step is not None else "-"
        self.etl_phase = get_phase_from_step(
            etl_step) if etl_step is not None else "-"

    def update_step(self, etl_step: EtlStepType) -> None:
        self.etl_step = step_to_str(etl_step)
        self.etl_phase = get_phase_from_step(etl_step)

    def update_run_id(self, etl_run_id: str) -> None:
        self.etl_run_id = etl_run_id

    def update_source_db_name(self, source_db_name: str) -> None:
        self.source_db_name = source_db_name

    def to_bind_kwargs(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
