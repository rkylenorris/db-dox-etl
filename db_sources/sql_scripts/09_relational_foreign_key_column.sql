-- 09_relational_foreign_key_column.sql
-- Extracts column-level foreign key mapping for relational.foreign_key_column.
-- NOTE: 'foreign_key_id' uses the FK constraint's object_id.
--       'column_id' and 'referenced_column_id' are column_id values in their respective tables.

SELECT
    fkc.constraint_object_id                        AS foreign_key_id,
    fkc.parent_column_id                            AS column_id,
    fkc.referenced_column_id                        AS referenced_column_id,
    fkc.constraint_column_id                        AS ordinal_position
FROM sys.foreign_key_columns AS fkc;
