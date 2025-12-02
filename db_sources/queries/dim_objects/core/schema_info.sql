-- 02_core_schema_info.sql
-- Extracts schema-level metadata for core.schema_info.
-- Run in the context of the database you want to document.

SELECT
    s.schema_id                   AS schema_id,
    DB_ID()                       AS database_id,
    s.name                        AS name,
    dp.name                       AS owner_name
FROM sys.schemas AS s
LEFT JOIN sys.database_principals AS dp
    ON dp.principal_id = s.principal_id;
