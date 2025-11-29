-- 12_relational_index_included_column.sql
-- Extracts index included column metadata for relational.index_included_column.
-- NOTE: 'index_id' here is the index_id from sys.indexes/sys.index_columns.

SELECT
    ic.object_id                                   AS table_id,
    ic.index_id                                    AS index_id,
    ic.column_id                                   AS column_id
FROM sys.index_columns AS ic
WHERE ic.is_included_column = 1;
