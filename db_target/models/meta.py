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

from ..base import Base

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
    name: Mapped[str] = mapped_column(String(128), nullable=False)
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
    environment: Mapped[str] = mapped_column(
        String(64), nullable=False)  # e.g. "development", "production"
    trigger_type: Mapped[str] = mapped_column(String(
        64), nullable=False, default="SCHEDULED")  # e.g. "manual", "scheduled", "event"
    # e.g. username or system that triggered the run
    triggered_by: Mapped[str | None] = mapped_column(String(128))
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=get_utc_now())
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False))
    status: Mapped[str] = mapped_column(
        # e.g. "IN_PROGRESS", "COMPLETED", "FAILED"
        String(32), nullable=False, default="IN_PROGRESS")
    total_rows_read: Mapped[int | None] = mapped_column(BigInteger)
    total_rows_written: Mapped[int | None] = mapped_column(BigInteger)
    error_count: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[str | None] = mapped_column(Text())

    step_audits: Mapped[list["ETLStepAudit"]
                        ] = relationship(back_populates="run")


class ETLStepAudit(Base):
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
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="IN_PROGRESS")
    error_message: Mapped[str | None] = mapped_column(Text())

    step_context: Mapped[dict | None] = mapped_column(
        JSON())  # Additional context as JSON

    run: Mapped[ETLRunAudit] = relationship(back_populates="step_audits")
    etl_step: Mapped[ETLStep | None] = relationship(
        back_populates="step_audits")
