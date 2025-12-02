-- 13_code_view_info.sql
-- Extracts view-level metadata for code.view_info.
-- NOTE: 'object_id' here is the view's object_id from sys.views.

SELECT
    v.object_id                                    AS object_id,
    CASE WHEN EXISTS (
        SELECT 1
        FROM sys.indexes AS i
        WHERE i.object_id = v.object_id
          AND i.index_id > 0
    ) THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END  AS is_indexed,
    CASE WHEN OBJECTPROPERTY(v.object_id, 'IsSchemaBound') = 1 THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_schema_bound,
    CASE WHEN OBJECTPROPERTY(v.object_id, 'IsViewWithCheckOption') = 1 THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS with_check_option
FROM sys.views AS v;
