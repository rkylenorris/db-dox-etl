from typing import Union
from enum import StrEnum, Enum


class EtlStep(StrEnum):
    """
    Summary:
        Enumeration of discrete ETL steps used for logging, tracing, and metrics.
        This enum provides a canonical set of step identifiers that represent
        meaningful phases and sub-steps in the ETL process. Each member is a
        string-backed enum (StrEnum) so it can be compared to and serialized as a
        regular string when storing logs, emitting metrics, or tagging events.
    """
    PIPELINE = "pipeline.main"

    # Phase 1 – Source metadata extraction
    EXTRACT_SYS_SCHEMAS = "extract.sys.schemas"
    EXTRACT_SYS_TABLES = "extract.sys.tables"
    EXTRACT_SYS_COLUMNS = "extract.sys.columns"
    EXTRACT_SYS_FKS = "extract.sys.foreign_keys"
    EXTRACT_SYS_INDEXES = "extract.sys.indexes"
    EXTRACT_SYS_VIEWS = "extract.sys.views"
    EXTRACT_SYS_PROCS = "extract.sys.procedures"
    EXTRACT_SYS_FUNCS = "extract.sys.functions"

    # Phase 2 – Parsing & relationship discovery
    PARSE_VIEW_DEFS = "parse.view.definitions"
    PARSE_PROC_DEFS = "parse.proc.definitions"
    PARSE_FUNC_DEFS = "parse.func.definitions"
    PARSE_RELATIONSHIPS = "parse.relationships"

    # Phase 3 – Transform into dimensional model
    TRANSFORM_DIM_OBJECTS = "transform.dim_objects"
    TRANSFORM_DIM_COLUMNS = "transform.dim_columns"
    TRANSFORM_FACT_RELATIONSHIPS = "transform.fact_relationships"
    TRANSFORM_AUDIT = "transform.audit"

    # Phase 4 – Load into doc DB
    LOAD_DIM_OBJECTS = "load.docdb.dim_objects"
    LOAD_DIM_COLUMNS = "load.docdb.dim_columns"
    LOAD_FACT_RELATIONS = "load.docdb.fact_relationships"
    LOAD_AUDIT = "load.docdb.audit"


# an either/or type so the helper function step_to_str can accept strings or enums
EtlStepType = Union[str, EtlStep]


def step_to_str(step: EtlStepType) -> str:
    """
    Convert EtlStep enum to string if needed.

    Args:
        step (EtlStepType): The ETL step as either a string or EtlStep enum.
    Returns:
        str: The ETL step as a string."""

    if isinstance(step, Enum):
        return step.value
    return step


def get_phase_from_step(step: EtlStepType) -> str:
    """
    Derive the high-level ETL phase from a detailed ETL step.

    Args:
        step (EtlStepType): The ETL step as either a string or EtlStep enum.
    Returns:
        str: The high-level ETL phase (e.g. 'extract', 'parse', 'transform', 'load').
    """
    step_str = step_to_str(step)
    return step_str.split(".")[0]  # phase is the first index
