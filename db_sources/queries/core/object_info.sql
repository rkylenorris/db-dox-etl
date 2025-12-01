-- 03_core_object_info.sql
-- Extracts object-level metadata for core.object_info.
-- Includes tables, views, procedures, functions, sequences, triggers, types, etc.
-- Run in the context of the database you want to document.

SELECT
    o.object_id                                      AS object_id,
    DB_ID()                                         AS database_id,
    o.schema_id                                     AS schema_id,
    o.name                                          AS object_name,
    CASE
        WHEN o.type IN ('U') THEN 'TABLE'
        WHEN o.type IN ('V') THEN 'VIEW'
        WHEN o.type IN ('P', 'X') THEN 'PROCEDURE'
        WHEN o.type IN ('FN', 'IF', 'TF', 'FS', 'FT') THEN 'FUNCTION'
        WHEN o.type IN ('SQ') THEN 'SEQUENCE'
        WHEN o.type IN ('AF', 'C', 'D', 'F', 'PK', 'UQ', 'EC', 'S', 'IT', 'TT') THEN 'TYPE'
        WHEN o.type IN ('TR', 'TA') THEN 'TRIGGER'
        ELSE 'OTHER'
    END                                             AS object_type,
    OBJECT_DEFINITION(o.object_id)                  AS definition,
    o.create_date                                   AS created_at,
    o.modify_date                                   AS modified_at,
    CASE 
        WHEN o.is_ms_shipped = 1 
             OR OBJECTPROPERTY(o.object_id, 'IsMSShipped') = 1
             OR OBJECT_SCHEMA_NAME(o.object_id) IN ('sys','INFORMATION_SCHEMA')
        THEN CAST(1 AS bit)
        ELSE CAST(0 AS bit)
    END                                             AS is_system,
    o.is_ms_shipped                                 AS is_ms_shipped,
    CASE 
        WHEN o.type IN ('TR', 'TA') 
             AND OBJECTPROPERTY(o.object_id, 'ExecIsTriggerDisabled') = 1
        THEN CAST(0 AS bit)
        ELSE CAST(1 AS bit)
    END                                             AS is_enabled
FROM sys.objects AS o;
