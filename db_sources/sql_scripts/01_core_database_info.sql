-- 01_core_database_info.sql
-- Extracts database-level metadata for core.database_info.
-- Run this in the context of the database you want to document.
-- NOTE: database_id is taken from sys.databases; is_primary is 1 for the current DB.

SELECT
    d.database_id                             AS database_id,
    d.name                                    AS name,
    d.collation_name                          AS collation_name,
    d.compatibility_level                     AS compatibility_lvl,
    d.recovery_model_desc                     AS recovery_model,
    SUSER_SNAME(d.owner_sid)                  AS owner_name,
    d.create_date                             AS created_at,
    b.last_backup_at                          AS last_backup_at,
    fg.name                                   AS default_file_group,
    d.containment_desc                        AS containment_desc,
    CASE WHEN d.database_id = DB_ID() THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_primary
FROM sys.databases AS d
OUTER APPLY (
    SELECT MAX(backup_finish_date) AS last_backup_at
    FROM msdb.dbo.backupset bs
    WHERE bs.database_name = d.name
) AS b
OUTER APPLY (
    SELECT TOP (1) fg.name
    FROM sys.filegroups fg
    WHERE fg.is_default = 1
) AS fg
WHERE d.database_id = DB_ID();  -- remove this filter to return all databases
