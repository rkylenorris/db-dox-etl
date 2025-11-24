# ETL Logging (loguru-based)

This module centralizes logging for the db-dox ETL using Loguru. It provides a consistent, structured logging configuration, bridges the standard library `logging` into Loguru, and offers helpers to bind ETL runtime context (app name, source database, step, run GUID) to log entries.

This README documents the public API, configuration, and usage examples for `etl_logging`.

## Why this module

- Centralized configuration: single place to configure console, file, and optional JSON logs.
- Structured context: bindings for `app_name`, `source_db_name`, `etl_step`, `etl_phase`, and an `etl_run_guid` make logs easy to query and correlate across steps.
- Library compatibility: routes stdlib `logging` (used by many dependencies) into Loguru to avoid split outputs.
- Convenience helpers: `get_etl_logger()` and `log_etl_step()` decorator to keep step logs consistent.

## Location

- Module: `etl_logging/etl_logging.py`
- Constants file: `etl_logging/etl_log_constants.json` (loaded at import time into `CONSTANTS`)

## Configuration file schema

`etl_log_constants.json` contains the runtime logging settings used by `get_constants()` and the module-level `CONSTANTS`. Example:

```json
{
  "app_name": "db-dox-phase-1-etl",
  "console_log_level": "INFO",
  "file_log_level": "DEBUG",
  "log_directory": "/logs",
  "json_log": true
}
```

- `app_name`: friendly name used in bound extras and log file names.
- `console_log_level`: log level for stderr console sink (e.g. `INFO`, `DEBUG`).
- `file_log_level`: log level for file sinks.
- `log_directory`: directory where log files are written (created automatically by `configure_logging`).
- `json_log`: whether to enable structured JSON file output.

## Public API

- `CONSTANTS` — module-level `ETLLogConstants` instance loaded from `etl_log_constants.json`.
- `generate_etl_run_guid()` -> `str` — create a new run GUID (UUID4 as string).
- `get_constants(path: Path)` -> `ETLLogConstants` — load constants from JSON file.
- `configure_logging(logging_constants: ETLLogConstants = CONSTANTS) -> None` — initialize Loguru sinks and route stdlib logging.
- `get_etl_logger(logger_context: Optional[ETLLogContext] = None)` -> `loguru.logger` — returns a logger bound with ETL context (app_name, source_db_name, etl_step, etc.).
- `log_etl_step(log_context: ETLLogContext)` -> decorator — decorator to wrap an ETL step; logs start, completion, duration, and exceptions.

Internally the module also exposes `InterceptHandler` and `intercept_stdlib_logging()` which route the standard library `logging` into Loguru.

## Usage examples

1) Basic initialization

```python
from pathlib import Path
from etl_logging import configure_logging, get_constants

# load constants from repo file (module does this by default too)
constants = get_constants(Path(__file__).parent / "etl_logging" / "etl_log_constants.json")

configure_logging(constants)

# later
from etl_logging import get_etl_logger
log = get_etl_logger()
log.info("ETL runner started")
```

2) Bind ETL context per-step

```python
from etl_logging import get_etl_logger
from etl_logging.etl_log_context import ETLLogContext

ctx = ETLLogContext(
    source_db_name="MySourceDB",
    etl_phase="extract",
    etl_step="extract.sys.tables",
)

step_logger = get_etl_logger(ctx)
step_logger.info("Reading table metadata")
```

3) Using the `log_etl_step()` decorator

```python
from etl_logging import log_etl_step
from etl_logging.etl_log_context import ETLLogContext

ctx = ETLLogContext(source_db_name="MyDb", etl_phase="extract", etl_step="extract.sys.tables")

@log_etl_step(ctx)
def extract_tables(conn):
    # logic here
    return []

# When called, this will log start/completion/duration and exceptions with full tracebacks.
extract_tables(conn)
```

4) Structured JSON logs

If `json_log` is enabled in `etl_log_constants.json`, a JSON file sink will be added. Each record will include the bound extras like `app_name` and `etl_run_guid` making downstream processing and ingestion into logging systems easy.

## Notes and best practices

- The module binds `app_name` and `etl_run_guid` globally when `configure_logging()` runs. Use `get_etl_logger()` to bind step-specific context such as `source_db_name`, `etl_phase`, and `etl_step`.
- When you need to generate the same `etl_run_guid` across modules, create it once with `generate_etl_run_guid()` (or read from environment) and pass it into a constants-like object or `ETLLogContext`.
- By default the module routes stdlib `logging` into Loguru. Avoid adding additional `logging.basicConfig` calls after `configure_logging()` unless you understand how the handlers interact.
- For high-throughput, the file sinks use `enqueue=True` which is safe for multiprocessing.

## Troubleshooting

- If logs are missing, ensure `configure_logging()` has been called before spawning worker processes, or call it in each process (sinks will be recreated).
- If JSON logs look incomplete, check that `json_log` is `true` in `etl_log_constants.json` and the process has write permission to `log_directory`.
