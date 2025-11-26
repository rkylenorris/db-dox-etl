from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .meta_enums import JobEnv, RunTriggerType, Status
from ...base import Base

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
        name (str): Name of the ETL phase.
        description (str | None): Optional description of the phase.
        created_at (datetime): Timestamp of creation in UTC.
        last_updated_at (datetime): Timestamp of last update in UTC.

        steps (list[ETLStep]): Relationship to ETLStep models associated with this phase."""
    __tablename__ = "etl_phase"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now()
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now(), onupdate=get_utc_now()
    )

    steps: Mapped[list["ETLStep"]] = relationship(back_populates="phase")


class ETLStep(Base):
    """
    ETL Step model representing detailed steps within ETL phases.
    Attributes:
        id (int): Primary key identifier.
        phase_id (int): Foreign key to the ETLPhase model.
        name (str): Name of the ETL step.
        description (str | None): Optional description of the step.
        created_at (datetime): Timestamp of creation in UTC.
        last_updated_at (datetime): Timestamp of last update in UTC.

        phase (ETLPhase): Relationship to the parent ETLPhase model.
    """
    __tablename__ = "etl_step"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    phase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{SCHEMA}.etl_phase.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now()
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now(), onupdate=get_utc_now()
    )

    phase: Mapped[ETLPhase] = relationship(back_populates="steps")
    step_audits: Mapped[list["ETLStepAudit"]
                        ] = relationship(back_populates="etl_step")


class ETLRunAudit(Base):
    """
    ETL Run Audit model representing an audit record for each ETL run.
    Attributes:
        etl_run_id (int): Primary key identifier for the ETL run.
        etl_run_guid (str): Unique GUID for the ETL run.
        job_name (str): Name of the ETL job.
        environment (str): Environment in which the ETL is run.
        trigger_type (str): Type of trigger for the ETL run.
        triggered_by (str | None): Identifier of who or what triggered the run.
        start_time (datetime): Start time of the ETL run in UTC.
        end_time (datetime | None): End time of the ETL run in UTC.
        status (str): Status of the ETL run.
        total_rows_read (int | None): Total number of rows read during the run.
        total_rows_written (int | None): Total number of rows written during the run.
        error_count (int | None): Number of errors encountered during the run.
        comments (str | None): Additional comments about the ETL run.

        step_audits (list[ETLStepAudit]): Relationship to ETLStepAudit models associated with this run.
    """
    __tablename__ = "etl_run_audit"
    __table_args__ = (
        UniqueConstraint("etl_run_guid", name="uq_etl_run_guid"),
        {"schema": SCHEMA}
    )

    etl_run_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    etl_run_guid: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True)
    job_name: Mapped[str] = mapped_column(
        String(256), nullable=False)  # e.g. "db_dox_etl_adventureworks"
    environment: Mapped[JobEnv] = mapped_column(
        # e.g. "development", "production"
        String(64), nullable=False, default=JobEnv.DEVELOPMENT.value)
    trigger_type: Mapped[RunTriggerType] = mapped_column(String(
        # e.g. "manual", "scheduled", "event"
        64), nullable=False, default=RunTriggerType.SCHEDULED.value)
    # e.g. username or system that triggered the run
    triggered_by: Mapped[str | None] = mapped_column(String(128))
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now())
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False))
    status: Mapped[Status] = mapped_column(
        # e.g. "IN_PROGRESS", "COMPLETED", "FAILED"
        String(32), nullable=False, default=Status.IN_PROGRESS.value)
    total_rows_read: Mapped[int | None] = mapped_column(BigInteger)
    total_rows_written: Mapped[int | None] = mapped_column(BigInteger)
    error_count: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[str | None] = mapped_column(Text())

    step_audits: Mapped[list["ETLStepAudit"]
                        ] = relationship(back_populates="run")


class ETLStepAudit(Base):
    """
    ETL Step Audit model representing an audit record for each ETL step within a run.
    Attributes:
        etl_step_audit_id (int): Primary key identifier for the ETL step audit.
        etl_run_id (int): Foreign key to the ETLRunAudit model.
        etl_step_id (int | None): Foreign key to the ETLStep model.
        target_db (str | None): Target database name.
        target_schema (str | None): Target schema name.
        target_object (str | None): Target object name.
        rows_read (int | None): Number of rows read during the step.
        rows_written (int | None): Number of rows written during the step.
        start_time (datetime): Start time of the ETL step in UTC.
        end_time (datetime | None): End time of the ETL step in UTC.
        status (str): Status of the ETL step.
        error_message (str | None): Error message if the step failed.
        step_context (dict | None): Additional context for the step as JSON.

        run (ETLRunAudit): Relationship to the parent ETLRunAudit model.
        etl_step (ETLStep | None): Relationship to the ETLStep model.
    """
    __tablename__ = "etl_step_audit"
    __table_args__ = (
        {"schema": SCHEMA}
    )

    etl_step_audit_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    etl_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f"{SCHEMA}.etl_run_audit.etl_run_id"), nullable=False
    )
    etl_step_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{SCHEMA}.etl_step.id"), nullable=True
    )

    target_db: Mapped[str | None] = mapped_column(String(256))
    target_schema: Mapped[str | None] = mapped_column(String(256))
    target_object: Mapped[str | None] = mapped_column(String(256))

    rows_read: Mapped[int | None] = mapped_column(BigInteger)
    rows_written: Mapped[int | None] = mapped_column(BigInteger)

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now())
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))

    # e.g. "IN_PROGRESS", "COMPLETED", "FAILED"
    status: Mapped[Status] = mapped_column(
        String(32), nullable=False, default=Status.IN_PROGRESS.value)
    error_message: Mapped[str | None] = mapped_column(Text())

    step_context: Mapped[dict | None] = mapped_column(
        JSON())  # Additional context as JSON

    run: Mapped[ETLRunAudit] = relationship(back_populates="step_audits")
    etl_step: Mapped[ETLStep | None] = relationship(
        back_populates="step_audits")
