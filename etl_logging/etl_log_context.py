from enum import StrEnum
from typing import Optional
from dataclasses import dataclass, asdict

from app_settings import get_app_settings, AppSettings, LogLevel
from definitions import EtlPhaseDefinition, EtlStepDefinition, get_phase_of_step


settings = get_app_settings()


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
    etl_phase: str
    etl_step: str
    etl_run_guid: str = settings.log.run_guid

    def __init__(self, source_db_name: Optional[str] = None,
                 etl_step: Optional[EtlStepDefinition] = None):
        self.source_db_name = source_db_name if source_db_name is not None else "-"
        self.etl_step = etl_step.code if etl_step is not None else "-"
        self.etl_phase = get_phase_of_step(
            etl_step).name if etl_step is not None else "-"

    def update_step(self, etl_step: EtlStepDefinition) -> None:
        self.etl_step = etl_step.code
        self.etl_phase = get_phase_of_step(etl_step).name

    def update_source_db_name(self, source_db_name: str) -> None:
        self.source_db_name = source_db_name

    def to_bind_kwargs(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
