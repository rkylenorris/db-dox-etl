-- 14_code_view_column.sql
-- Extracts view column metadata for code.view_column.
-- NOTE: 'view_id' here is the view's object_id from sys.views.
--       source_expression and source_column_id are left NULL for parser-based enrichment.

SELECT
    c.object_id                                   AS view_id,
    c.name                                        AS column_name,
    c.column_id                                   AS ordinal_position,
    t.name                                        AS data_type,
    CAST(NULL AS nvarchar(max))                   AS source_expression,
    CAST(NULL AS int)                             AS source_column_id
FROM sys.columns AS c
INNER JOIN sys.views AS v
    ON v.object_id = c.object_id
INNER JOIN sys.types AS t
    ON t.user_type_id = c.user_type_id;
