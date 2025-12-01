-- 17_code_procedure_result_column.sql
-- Extracts first-result-set metadata for stored procedures for code.procedure_result_column.
-- Uses sys.dm_exec_describe_first_result_set_for_object.

SELECT
    p.object_id                                   AS procedure_id,
    rs.name                                       AS column_name,
    rs.column_ordinal                             AS ordinal_position,
    rs.system_type_name                           AS data_type,
    rs.source_id                                  AS source_object_id
FROM sys.procedures AS p
CROSS APPLY sys.dm_exec_describe_first_result_set_for_object(p.object_id, NULL) AS rs
WHERE rs.error_number IS NULL;
