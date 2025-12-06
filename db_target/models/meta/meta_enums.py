from enum import Enum


class PhaseType(str, Enum):
    APPLICATION = "application"
    PIPELINE = "pipeline"
    AUDIT = "audit"


class StepType(str, Enum):
    APPLICATION_PIPELINE_START = "application.pipeline.start"
    APPLICATION_PIPELINE_END = "application.pipeline.end"
    PIPELINE_DOCDB_DIM_OBJECTS = "pipeline.docdb.dim_objects"
    PIPELINE_DOCDB_DIM_COLUMNS = "pipeline.docdb.dim_columns"
    PIPELINE_DOCDB_FACT_RELATIONSHIPS = "pipeline.docdb.fact_relationships"
    AUDIT_DOCDB_LOAD = "audit.docdb.load"


class ETLEnvironmentType(str, Enum):
    DEV = "DEV"
    TEST = "TEST"
    QA = "QA"
    PROD = "PROD"


class ETLStatusCodeType(str, Enum):
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"


class ETLTriggerType(str, Enum):
    SCHEDULED = "SCHEDULED"
    MANUAL = "MANUAL"
    API = "API"
