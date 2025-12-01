-- 18_code_function_info.sql
-- Extracts function metadata for code.function_info.
-- NOTE: 'object_id' here is the function's object_id from sys.objects.

SELECT
    o.object_id                                   AS object_id,
    CASE 
        WHEN o.type IN ('FN', 'FS') THEN 'SCALAR'
        WHEN o.type IN ('IF') THEN 'INLINE_TVF'
        WHEN o.type IN ('TF', 'FT') THEN 'MULTI_TVF'
        ELSE 'OTHER'
    END                                           AS function_type,
    ret_type.name                                 AS return_data_type,
    CASE WHEN OBJECTPROPERTY(o.object_id, 'IsSchemaBound') = 1 THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_schema_bound,
    CASE WHEN OBJECTPROPERTY(o.object_id, 'IsDeterministic') = 1 THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_deterministic
FROM sys.objects AS o
OUTER APPLY (
    SELECT TOP (1) prm.user_type_id
    FROM sys.parameters AS prm
    WHERE prm.object_id = o.object_id
      AND prm.parameter_id = 0         -- return value
) AS rp
LEFT JOIN sys.types AS ret_type
    ON ret_type.user_type_id = rp.user_type_id
WHERE o.type IN ('FN','FS','TF','FT','IF');
