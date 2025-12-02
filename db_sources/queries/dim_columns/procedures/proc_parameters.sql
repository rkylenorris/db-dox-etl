-- 16_code_procedure_parameter.sql
-- Extracts stored procedure parameter metadata for code.procedure_parameter.
-- NOTE: 'procedure_id' here is the procedure's object_id from sys.procedures.

SELECT
    p.object_id                                   AS procedure_id,
    prm.name                                      AS parameter_name,
    t.name                                        AS data_type,
    prm.max_length                                AS max_length,
    prm.precision                                 AS precision,
    prm.scale                                     AS scale,
    CASE WHEN prm.is_output = 1 THEN 'OUT' ELSE 'IN' END AS parameter_mode,
    prm.parameter_id                              AS ordinal_position,
    prm.has_default_value                         AS has_default_value,
    CAST(prm.default_value AS nvarchar(max))      AS default_value
FROM sys.procedures AS p
INNER JOIN sys.parameters AS prm
    ON prm.object_id = p.object_id
   AND prm.parameter_id <> 0      -- exclude return value (for functions)
INNER JOIN sys.types AS t
    ON t.user_type_id = prm.user_type_id;
