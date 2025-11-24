"""
etl_logging.py

Logging setup for db-dox-phase-1-etl.

Phase 1 focus:
- Gather database metadata (system tables, views, procedures, etc.)
- Transform / normalize metadata
- Load into a documentation database

This module centralizes Loguru configuration and provides helpers for:
- ETL context (db_name, etl_step, run_id)
- Standard library logging interception
- Step-level decorators for timing and error logging
"""

import sys
import time
import logging
import json

from pathlib import Path
from functools import wraps
from loguru import logger as _base_logger
from typing import Callable, Optional, Any
from dataclasses import dataclass
from uuid import uuid4

from .etl_log_context import LogLevel, ETLLogContext


def generate_etl_run_guid() -> str:
    """Generate a new ETL run GUID as a string."""
    return str(uuid4())


@dataclass
class ETLLogConstants:
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
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ETLLogConstants(**data)


# constants
CONSTANTS = get_constants(Path(__file__).parent / "etl_log_constants.json")


# --- Intercept standard logging and redirect to Loguru ------------------------


class InterceptHandler(logging.Handler):
    """Redirect standard logging calls into Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = _base_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Forward to Loguru, preserving exception info
        _base_logger.opt(
            depth=6,
            exception=record.exc_info
        ).log(level, record.getMessage())


def intercept_stdlib_logging() -> None:
    """
    Route the stdlib `logging` module logs (used by many libraries) into Loguru.
    This avoids split outputs between two logging systems.
    """
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = [InterceptHandler()]


# --- Base logger with default extra fields ------------------------------------


def _add_default_extra(record: Any) -> None:
    """
    Ensure our ETL context fields exist so format strings don't explode
    when they aren't bound.
    """
    extra = record["extra"]
    extra.setdefault("app_name", "-")
    extra.setdefault("source_db_name", "-")
    extra.setdefault("etl_run_guid", "-")
    extra.setdefault("etl_run_id", "-")
    extra.setdefault("etl_phase", "-")
    extra.setdefault("etl_step", "-")

    # No return; we mutate in place


# This is the base logger patched with default extras.
logger = _base_logger.patch(_add_default_extra)


# --- Public configuration function -------------------------------------------


def configure_logging(
    logging_constants: ETLLogConstants = CONSTANTS
) -> None:
    """
    Configure Loguru logging for db-dox-phase-1-etl.

    Parameters:
        log_dir (str): Directory for log files.
        app_name (str): Name of the app for context (in JSON logs etc.).
        console_log_level (str): Level for console output.
        file_log_level (str): Level for file output.
        json_log (bool): Whether to output structured JSON logs.
    """
    logging_constants.log_directory.mkdir(parents=True, exist_ok=True)

    # Remove all existing sinks
    logger.remove()

    # --- Console Sink (human-friendly) ---
    logger.add(
        sys.stderr,
        level=logging_constants.console_log_level.value,
        colorize=True,
        backtrace=True,
        diagnose=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{extra[source_db_name]: <25} | "
            "{extra[etl_phase]: <25} | "
            "{extra[etl_step]: <25} | "
            "{message}"
        ),
    )

    # --- Rotating File Sink (text) ---
    logger.add(
        logging_constants.log_directory / f"{logging_constants.app_name}.log",
        level=logging_constants.file_log_level.value,
        rotation="7 days",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,  # safe for multiprocessing
        backtrace=True,
        diagnose=False,
    )

    # --- JSON Structured Logs (optional) ---
    if logging_constants.json_log:
        logger.add(
            logging_constants.log_directory /
            f"{logging_constants.app_name}.json",
            level=logging_constants.file_log_level.value,
            rotation="7 days",
            retention="30 days",
            encoding="utf-8",
            enqueue=True,
            serialize=True,  # output JSON
        )

    # Route stdlib logging (for libraries) into Loguru
    intercept_stdlib_logging()

    # Bind app_name globally (available in JSON extra)
    global logger  # type: ignore
    logger = logger.bind(app_name=logging_constants.app_name)
    logger = logger.bind(etl_run_guid=logging_constants.run_guid)


# --- Helpers for ETL context --------------------------------------------------


def get_etl_logger(
    logger_context: Optional[ETLLogContext] = None
):
    """
    Return a logger bound with ETL context.

    Example:
        run_id = "2025-11-23T1600Z"
        db_logger = get_etl_logger(
            db_name="MySourceDb",
            etl_step="extract.sys.tables",
            run_id=run_id,
        )
        db_logger.info("Extracting table metadata")
    """
    if logger_context is None:
        logger_context = ETLLogContext()

    return logger.bind(**logger_context.to_bind_kwargs())


def log_etl_step(
    log_context: ETLLogContext
):
    """
    Decorator to log the life cycle of a specific ETL step.

    - Logs start + end + duration
    - Includes etl_step, db_name, and optional run_id in context
    - Logs full traceback on failure

    Example:
        @log_etl_step("extract.sys.tables", db_name="MyDb")
        def extract_sys_tables(conn):
            ...

    With a dynamic run_id:
        run_id = uuid4().hex
        def get_run_id(): return run_id

        @log_etl_step("parse.procedures", db_name="MyDb", run_id_getter=get_run_id)
        def parse_procedures(...):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            step_logger = get_etl_logger(
                log_context
            )

            start = time.perf_counter()
            step_logger.info("Starting ETL step")
            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start
                step_logger.info(f"Completed ETL step in {duration:.2f}s")
                return result
            except Exception:
                duration = time.perf_counter() - start
                step_logger.exception(
                    f"ETL step failed after {duration:.2f}s"
                )
                raise

        return wrapper

    return decorator
