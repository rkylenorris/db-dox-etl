-- 15_code_procedure_info.sql
-- Extracts stored procedure metadata for code.procedure_info.
-- NOTE: 'object_id' here is the procedure's object_id from sys.procedures.

SELECT
    p.object_id                                   AS object_id,
    p.is_encrypted                                AS is_encrypted,
    dp.name                                       AS execute_as,
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM sys.dm_exec_describe_first_result_set_for_object(p.object_id, NULL) AS rs
            WHERE rs.error_number IS NULL
        )
        THEN CAST(1 AS bit)
        ELSE CAST(0 AS bit)
    END                                           AS has_result_set
FROM sys.procedures AS p
LEFT JOIN sys.database_principals AS dp
    ON dp.principal_id = p.execute_as_principal_id;
