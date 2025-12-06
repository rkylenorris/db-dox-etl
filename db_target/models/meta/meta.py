from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    Index,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base import Base
from .meta_enums import (
    ETLEnvironmentType,
    ETLStatusCodeType,
    ETLTriggerType,
    PhaseType,
    StepType,
)

# constants; schema name and timezone for date fields
SCHEMA = "meta"
TIMEZONE = timezone.utc


def get_utc_now() -> datetime:
    """
    Get the current UTC datetime with timezone info.
    Returns:
        datetime: Current UTC datetime.
    """
    return datetime.now(tz=TIMEZONE)


class ETLPhase(Base):
    """
    ETL Phase model representing different phases of the ETL process.

    Attributes:
        id (int): Primary key identifier.
        phase_type (str): Enum-like phase identifier (application/pipeline/audit).
        display_name (str): Human-readable name of the phase.
        description (str | None): Optional description of the phase.
        sort_order (int): Execution order for the phase.
        created_at (datetime): Timestamp of creation in UTC.
        last_updated_at (datetime): Timestamp of last update in UTC.

        steps (list[ETLStep]): Relationship to ETLStep models associated with this phase."""
    __tablename__ = "etl_phase"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    phase_type: Mapped[PhaseType] = mapped_column(
        SAEnum(
            PhaseType,
            name="phase_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        unique=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now, onupdate=get_utc_now
    )

    steps: Mapped[list["ETLStep"]] = relationship(back_populates="phase")


class ETLStep(Base):
    """
    ETL Step model representing detailed steps within ETL phases.
    Attributes:
        id (int): Primary key identifier.
        etl_phase_id (int): Foreign key to the ETLPhase model.
        step_type (str): Enum-like step identifier.
        display_name (str): Human-readable name of the step.
        step_order (int): Order of the step within a phase.
        is_active (bool): Soft-deactivation flag.
        description (str | None): Optional description of the step.
        created_at (datetime): Timestamp of creation in UTC.
        last_updated_at (datetime): Timestamp of last update in UTC.

        phase (ETLPhase): Relationship to the parent ETLPhase model.
    """
    __tablename__ = "etl_step"
    __table_args__ = (
        Index("ix_etl_step_type", "step_type"),
        Index("ix_etl_step_phase_order", "etl_phase_id", "step_order"),
        {"schema": SCHEMA},
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    etl_phase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{SCHEMA}.etl_phase.id"), nullable=False)
    step_type: Mapped[StepType] = mapped_column(
        SAEnum(
            StepType,
            name="step_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        unique=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(150), nullable=False)
    step_order: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    description: Mapped[str | None] = mapped_column(Text())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now, onupdate=get_utc_now
    )

    phase: Mapped[ETLPhase] = relationship(back_populates="steps")
    step_audits: Mapped[list["ETLStepAudit"]
                        ] = relationship(back_populates="etl_step")


class ETLRunAudit(Base):
    """
    ETL Run Audit model representing an audit record for each ETL run.
    Attributes:
        id (int): Primary key identifier for the ETL run.
        etl_run_guid (str): Unique GUID for the ETL run.
        job_name (str): Name of the ETL job.
        environment (str): Environment in which the ETL is run.
        trigger_type (str): Type of trigger for the ETL run.
        trigger_user (str | None): Identifier of who or what triggered the run.
        start_time_utc (datetime): Start time of the ETL run in UTC.
        end_time_utc (datetime | None): End time of the ETL run in UTC.
        status_code (str): Status of the ETL run.
        total_rows_read (int | None): Total number of rows read during the run.
        total_rows_written (int | None): Total number of rows written during the run.
        error_count (int | None): Number of errors encountered during the run.
        comments (str | None): Additional comments about the ETL run.

        step_audits (list[ETLStepAudit]): Relationship to ETLStepAudit models associated with this run.
    """
    __tablename__ = "etl_run_audit"
    __table_args__ = (
        UniqueConstraint("etl_run_guid", name="uq_etl_run_guid"),
        Index("ix_etl_run_job_start", "job_name", "start_time_utc"),
        {"schema": SCHEMA}
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    etl_run_guid: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True)
    job_name: Mapped[str] = mapped_column(String(128), nullable=False)
    environment: Mapped[ETLEnvironmentType] = mapped_column(
        SAEnum(
            ETLEnvironmentType,
            name="etl_environment_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )
    start_time_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now
    )
    end_time_utc: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False))
    status_code: Mapped[ETLStatusCodeType] = mapped_column(
        SAEnum(
            ETLStatusCodeType,
            name="etl_status_code_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=ETLStatusCodeType.STARTED,
    )
    total_rows_read: Mapped[int | None] = mapped_column(BigInteger)
    total_rows_written: Mapped[int | None] = mapped_column(BigInteger)
    error_count: Mapped[int | None] = mapped_column(Integer)
    trigger_type: Mapped[ETLTriggerType] = mapped_column(
        SAEnum(
            ETLTriggerType,
            name="etl_trigger_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=ETLTriggerType.SCHEDULED,
    )
    trigger_user: Mapped[str | None] = mapped_column(String(128))
    comments: Mapped[str | None] = mapped_column(Text())

    step_audits: Mapped[list["ETLStepAudit"]
                        ] = relationship(back_populates="run")


class ETLStepAudit(Base):
    """
    ETL Step Audit model representing an audit record for each ETL step within a run.
    Attributes:
        id (int): Primary key identifier for the ETL step audit.
        etl_run_id (int): Foreign key to the ETLRunAudit model.
        etl_phase_id (int): Foreign key to the ETLPhase model.
        step_id (int): Foreign key to the ETLStep model.
        step_order (int): Order of the ETL step within its phase.
        source_system (str | None): Source system name.
        source_object (str | None): Source object name.
        target_system (str | None): Target system name.
        target_object (str | None): Target object name.
        rows_read (int | None): Number of rows read during the step.
        rows_written (int | None): Number of rows written during the step.
        start_time_utc (datetime): Start time of the ETL step in UTC.
        end_time_utc (datetime | None): End time of the ETL step in UTC.
        status_code (str): Status of the ETL step.
        error_message (str | None): Error message if the step failed.
        extra_context_json (dict | None): Additional context for the step as JSON.

        run (ETLRunAudit): Relationship to the parent ETLRunAudit model.
        etl_step (ETLStep): Relationship to the ETLStep model.
    """
    __tablename__ = "etl_step_audit"
    __table_args__ = (
        Index("ix_etl_step_run_step", "etl_run_id", "step_order"),
        Index("ix_etl_step_time", "start_time_utc"),
        {"schema": SCHEMA}
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    etl_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f"{SCHEMA}.etl_run_audit.id"), nullable=False
    )
    etl_phase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{SCHEMA}.etl_phase.id"), nullable=False
    )
    step_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{SCHEMA}.etl_step.id"), nullable=False)

    source_system: Mapped[str | None] = mapped_column(String(100))
    source_object: Mapped[str | None] = mapped_column(String(256))
    target_system: Mapped[str | None] = mapped_column(String(100))
    target_object: Mapped[str | None] = mapped_column(String(256))

    rows_read: Mapped[int | None] = mapped_column(BigInteger)
    rows_written: Mapped[int | None] = mapped_column(BigInteger)

    start_time_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now
    )
    end_time_utc: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False))

    status_code: Mapped[ETLStatusCodeType] = mapped_column(
        SAEnum(
            ETLStatusCodeType,
            name="etl_status_code_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=ETLStatusCodeType.STARTED,
    )
    error_message: Mapped[str | None] = mapped_column(Text())
    extra_context_json: Mapped[dict | None] = mapped_column(JSON())

    run: Mapped[ETLRunAudit] = relationship(back_populates="step_audits")
    etl_step: Mapped[ETLStep] = relationship(back_populates="step_audits")
    phase: Mapped[ETLPhase] = relationship()
