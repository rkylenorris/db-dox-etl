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
import loguru
import logging

from pathlib import Path
from functools import wraps
from loguru import logger as _base_logger
from typing import Callable, Optional, Any

from .etl_log_context import ETLLogContext
from .etl_log_constants import ETLLogConstants, get_constants, DEFAULT_EXTRA_FIELDS


# constants
CONSTANTS = get_constants()


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
    Create ETL context records and add default values if missing.
    This ensures that all logs have a consistent set of extra fields.
    Args:
        record (Any): The Loguru log record to modify.
    """
    extra = record["extra"]

    for field in DEFAULT_EXTRA_FIELDS:
        extra.setdefault(field, "-")
    # No return; we mutate in place


# This is the base logger patched with default extras.
logger = _base_logger.patch(_add_default_extra)


# --- Public configuration function -------------------------------------------


def configure_logging(
    logging_constants: ETLLogConstants = CONSTANTS,
    logger: loguru.Logger = logger,
) -> loguru.Logger:
    """
    Configure Loguru logging for db-dox-phase-1-etl.

    Parameters:
        logging_constants (ETLLogConstants): Configuration constants for logging.
        logger (loguru.Logger): The Loguru logger instance to configure.
    Returns:
        loguru.Logger: The configured Loguru logger instance.
    """

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

    # Bind app_name globally (available in JSON extra) and return logger object
    return logger.bind(
        app_name=logging_constants.app_name,
        etl_run_guid=logging_constants.run_guid
    )


# --- Helpers for ETL context --------------------------------------------------


def get_etl_logger(
    logger_context: Optional[ETLLogContext] = None
) -> loguru.Logger:
    """
    Return a logger bound with ETL context.

    Args:
        logger_context (Optional[ETLLogContext]): The ETL context to bind.
            If None, a default context with placeholder values is used.
    Returns:
        loguru.Logger: A Loguru logger instance with ETL context bound.
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

    Args:
        log_context (ETLLogContext): The ETL context to bind for the step.
    Returns:
        Callable: The decorated function with ETL step logging.
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
