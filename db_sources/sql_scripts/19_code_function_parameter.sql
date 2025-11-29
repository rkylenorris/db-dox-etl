-- 19_code_function_parameter.sql
-- Extracts function parameter metadata for code.function_parameter.
-- NOTE: 'function_id' here is the function's object_id from sys.objects.

SELECT
    f.object_id                                   AS function_id,
    prm.name                                      AS parameter_name,
    t.name                                        AS data_type,
    prm.max_length                                AS max_length,
    prm.precision                                 AS precision,
    prm.scale                                     AS scale,
    CASE WHEN prm.is_output = 1 THEN 'OUT' ELSE 'IN' END AS parameter_mode,
    prm.parameter_id                              AS ordinal_position,
    prm.has_default_value                         AS has_default_value,
    CAST(prm.default_value AS nvarchar(max))      AS default_value
FROM sys.objects AS f
INNER JOIN sys.parameters AS prm
    ON prm.object_id = f.object_id
   AND prm.parameter_id <> 0      -- exclude return
INNER JOIN sys.types AS t
    ON t.user_type_id = prm.user_type_id
WHERE f.type IN ('FN','FS','TF','FT','IF');
