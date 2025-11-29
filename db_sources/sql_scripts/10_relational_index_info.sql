-- 10_relational_index_info.sql
-- Extracts index-level metadata for relational.index_info.
-- NOTE: 'table_id' here is the indexed object_id (usually a table or view).

SELECT
    i.object_id                                     AS table_id,
    i.index_id                                      AS index_id,
    i.name                                          AS index_name,
    CASE 
        WHEN i.type_desc LIKE '%CLUSTERED COLUMNSTORE%' THEN 'column_store'
        WHEN i.type_desc LIKE '%CLUSTERED%' THEN 'CLUSTERED'
        WHEN i.type_desc LIKE '%NONCLUSTERED%' THEN 'NONCLUSTERED'
        ELSE i.type_desc
    END                                             AS index_type,
    i.is_primary_key                                AS is_primary_key,
    i.is_unique                                     AS is_unique,
    i.has_filter                                    AS is_filtered,
    i.filter_definition                             AS filter_definition,
    CASE WHEN i.type_desc LIKE '%CLUSTERED%' THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_clustered,
    CASE WHEN i.type_desc LIKE '%COLUMNSTORE%' THEN CAST(1 AS bit) ELSE CAST(0 AS bit) END AS is_column_store,
    CAST(0 AS bit)                                  AS is_full_text,   -- full-text handled separately if needed
    fg.name                                         AS file_group_name,
    i.fill_factor                                   AS fill_factor,
    p.data_compression_desc                         AS compression_desc
FROM sys.indexes AS i
LEFT JOIN sys.partitions AS p
    ON p.object_id = i.object_id
   AND p.index_id  = i.index_id
   AND p.partition_number = 1
LEFT JOIN sys.data_spaces AS ds
    ON ds.data_space_id = i.data_space_id
LEFT JOIN sys.filegroups AS fg
    ON fg.data_space_id = ds.data_space_id
WHERE i.index_id > 0;  -- exclude heap (index_id = 0)
