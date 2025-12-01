-- 04_relational_table_info.sql
-- Extracts table-level metadata for relational.table_info.
-- NOTE: 'object_id' here is the source sys.tables.object_id.
--       table_type is defaulted to NULL/Other and can be curated later.

SELECT
    t.object_id                                     AS object_id,
    CAST(NULL AS varchar(64))                      AS table_type,      -- set to Fact/Dimension/etc. in curation step
    rc.row_count                                    AS row_count,
    CASE WHEN t.temporal_type = 2 THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_system_versioned,
    t.history_table_id                              AS history_table_id,
    t.is_external                                   AS is_external,
    ds.file_group_name                              AS file_group_name,
    CASE WHEN ds.partition_scheme_name IS NOT NULL THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_partitioned,
    ds.partition_scheme_name                        AS partition_scheme,
    ds.partition_function_name                      AS partition_function
FROM sys.tables AS t
OUTER APPLY (
    SELECT SUM(ps.row_count) AS row_count
    FROM sys.dm_db_partition_stats AS ps
    WHERE ps.object_id = t.object_id
      AND ps.index_id IN (0, 1)
) AS rc
OUTER APPLY (
    SELECT TOP (1)
        fg.name AS file_group_name,
        ps.name AS partition_scheme_name,
        pf.name AS partition_function_name
    FROM sys.indexes AS i
    INNER JOIN sys.data_spaces AS ds
        ON ds.data_space_id = i.data_space_id
    LEFT JOIN sys.filegroups AS fg
        ON fg.data_space_id = ds.data_space_id
    LEFT JOIN sys.partition_schemes AS ps
        ON ps.data_space_id = ds.data_space_id
    LEFT JOIN sys.partition_functions AS pf
        ON pf.function_id = ps.function_id
    WHERE i.object_id = t.object_id
      AND i.index_id IN (0,1)
    ORDER BY i.index_id
) AS ds;
