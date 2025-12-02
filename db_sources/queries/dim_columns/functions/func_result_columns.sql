-- 20_code_function_result_column.sql
-- Extracts first-result-set metadata for table-valued functions for code.function_result_column.
-- Uses sys.dm_exec_describe_first_result_set_for_object.

SELECT
    f.object_id                                   AS function_id,
    rs.name                                       AS column_name,
    rs.column_ordinal                             AS ordinal_position,
    rs.system_type_name                           AS data_type,
    rs.source_id                                  AS source_object_id
FROM sys.objects AS f
CROSS APPLY sys.dm_exec_describe_first_result_set_for_object(f.object_id, NULL) AS rs
WHERE f.type IN ('TF','FT','IF')
  AND rs.error_number IS NULL;
