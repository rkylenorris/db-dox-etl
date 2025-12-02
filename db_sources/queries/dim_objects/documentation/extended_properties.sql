-- 21_doc_extended_property.sql
-- Extracts extended property metadata for doc.extended_property.
-- Handles DATABASE, SCHEMA, OBJECT, and COLUMN scopes.

SELECT
    DB_ID()                                       AS database_id,
    CASE 
        WHEN ep.class_desc = 'DATABASE' THEN NULL
        WHEN ep.class_desc = 'SCHEMA'   THEN s.schema_id
        WHEN ep.class_desc = 'OBJECT_OR_COLUMN' THEN o.schema_id
        ELSE NULL
    END                                           AS schema_id,
    CASE 
        WHEN ep.class_desc = 'DATABASE' THEN NULL
        WHEN ep.class_desc = 'SCHEMA'   THEN NULL
        WHEN ep.class_desc = 'OBJECT_OR_COLUMN' THEN ep.major_id
        ELSE NULL
    END                                           AS object_id,
    CASE 
        WHEN ep.class_desc = 'OBJECT_OR_COLUMN' AND ep.minor_id <> 0 THEN ep.minor_id
        ELSE NULL
    END                                           AS column_id,
    CASE ep.class_desc
        WHEN 'DATABASE'         THEN 'DATABASE'
        WHEN 'SCHEMA'           THEN 'SCHEMA'
        WHEN 'OBJECT_OR_COLUMN' THEN CASE WHEN ep.minor_id = 0 THEN 'OBJECT' ELSE 'COLUMN' END
        ELSE ep.class_desc
    END                                           AS level_type,
    ep.name                                       AS property_name,
    CAST(ep.value AS nvarchar(max))               AS property_value
FROM sys.extended_properties AS ep
LEFT JOIN sys.objects AS o
    ON ep.class_desc = 'OBJECT_OR_COLUMN'
   AND ep.major_id   = o.object_id
LEFT JOIN sys.schemas AS s
    ON ep.class_desc = 'SCHEMA'
   AND ep.major_id   = s.schema_id;
