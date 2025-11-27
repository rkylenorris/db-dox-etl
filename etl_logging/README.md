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
- Constants module: `etl_logging/etl_log_constants.py` (provides `ETLLogConstants`, `get_constants`) and the JSON file `etl_logging/etl_log_constants.json` (loaded at import time into module-level `CONSTANTS`).

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

- `ETLLogConstants` — dataclass configuration object (defined in `etl_logging/etl_log_constants.py`).
- `get_constants(path: Path)` -> `ETLLogConstants` — loader factory (defined in `etl_logging/etl_log_constants.py`) that reads the JSON config.
- `constants_path` — module-level Path used to locate the JSON file when `CONSTANTS` is created.
- `CONSTANTS` — module-level `ETLLogConstants` instance, created at import time by calling `get_constants(constants_path)`.
- `generate_etl_run_guid()` -> `str` — create a new run GUID (UUID4 as string).
- `get_constants(path: Path)` -> `ETLLogConstants` — load constants from JSON file.
- `configure_logging(logging_constants: ETLLogConstants = CONSTANTS) -> None` — initialize Loguru sinks and route stdlib logging.
- `get_etl_logger(logger_context: Optional[ETLLogContext] = None)` -> `loguru.Logger` — returns a logger bound with an `ETLLogContext` instance. The context is used to bind `source_db_name`, `etl_run_id`, `etl_phase`, and `etl_step` into the logger's extra fields.
- `log_etl_step(log_context: ETLLogContext)` -> decorator — decorator to wrap an ETL step; logs start, completion, duration, and exceptions.

Internally the module also exposes `InterceptHandler` and `intercept_stdlib_logging()` which route the standard library `logging` into Loguru.

## Usage examples

### Basic initialization

```python
from pathlib import Path
from etl_logging import configure_logging, get_constants

# The module exposes a `CONSTANTS` object at import-time which loads
# `etl_log_constants.json`. You can also load constants manually.
from etl_logging import configure_logging, CONSTANTS

configure_logging(CONSTANTS)

# later
from etl_logging import get_etl_logger
log = get_etl_logger()
log.info("ETL runner started")
```

### Bind ETL context per-step

```python
from etl_logging import get_etl_logger
from etl_logging.etl_log_context import ETLLogContext

# ETLLogContext holds per-step runtime fields — note the `etl_run_id` field
# is separate from the global `etl_run_guid` created by `ETLLogConstants`.
ctx = ETLLogContext(
  source_db_name="MySourceDB",
  etl_run_id="run-2025-11-27T10:00Z",
  etl_step="extract.sys.tables",
)

step_logger = get_etl_logger(ctx)
step_logger.info("Reading table metadata")
```

### Using the `log_etl_step()` decorator

```python
from etl_logging import log_etl_step
from etl_logging.etl_log_context import ETLLogContext

ctx = ETLLogContext(source_db_name="MyDb", etl_run_id="2025-11-27-run", etl_step="extract.sys.tables")

@log_etl_step(ctx)
def extract_tables(conn):
    # logic here
    return []

# When called, this will log start/completion/duration and exceptions with full tracebacks.
extract_tables(conn)
```

### Structured JSON logs

If `json_log` is enabled in `etl_log_constants.json`, a JSON file sink will be added. Each record will include the bound extras like `app_name` and `etl_run_guid` making downstream processing and ingestion into logging systems easy.

## Notes and best practices

- The logging configuration stores two related concepts:
  - `etl_run_guid` (global GUID): created by `ETLLogConstants` at startup; it's bound globally during `configure_logging()` and is included on every log record as `etl_run_guid`.
  - `etl_run_id` (runtime/per-step id): part of `ETLLogContext` and used to identify a particular run or job instance (for example a timestamped run id). Bind it per-step with `get_etl_logger()` or via `log_etl_step()`.
- When you need to generate the same `etl_run_guid` across processes, generate it once and pass it in (or set it in `ETLLogConstants`/the JSON file) so all processes share the same GUID.
- By default the module routes stdlib `logging` into Loguru. Avoid adding additional `logging.basicConfig` calls after `configure_logging()` unless you understand how the handlers interact.
- For high-throughput, the file sinks use `enqueue=True` which is safe for multiprocessing.

## Troubleshooting

- If logs are missing, ensure `configure_logging()` has been called before spawning worker processes, or call it in each process (sinks will be recreated).
- If JSON logs look incomplete, check that `json_log` is `true` in `etl_log_constants.json` and the process has write permission to `log_directory`.
