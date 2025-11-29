-- 11_relational_index_column.sql
-- Extracts index key column metadata for relational.index_column.
-- NOTE: 'index_id' here is the index_id from sys.indexes/sys.index_columns.

SELECT
    ic.object_id                                   AS table_id,
    ic.index_id                                    AS index_id,
    ic.column_id                                   AS column_id,
    ic.key_ordinal                                 AS key_ordinal,
    ic.is_descending_key                           AS is_descending
FROM sys.index_columns AS ic
WHERE ic.key_ordinal > 0;   -- only key columns
