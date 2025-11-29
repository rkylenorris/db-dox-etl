-- 07_relational_constraint_column.sql
-- Extracts column mappings for constraints for relational.constraint_column.
-- NOTE: 'constraint_id' here is the constraint's object_id from the source database.
--       'column_id' here is the column_id within the table.

-- Columns participating in PRIMARY KEY and UNIQUE constraints
SELECT
    kc.object_id                                    AS constraint_id,
    ic.column_id                                    AS column_id,
    ic.key_ordinal                                  AS ordinal_position
FROM sys.key_constraints AS kc
INNER JOIN sys.index_columns AS ic
    ON ic.object_id = kc.parent_object_id
   AND ic.index_id  = kc.unique_index_id

UNION ALL

-- Columns participating in CHECK constraints
-- (no strict column ordering; ordinal_position is set to 1)
SELECT
    cc.object_id                                    AS constraint_id,
    c.column_id                                     AS column_id,
    1                                               AS ordinal_position
FROM sys.check_constraints AS cc
INNER JOIN sys.columns AS c
    ON c.object_id = cc.parent_object_id
   AND cc.parent_column_id = c.column_id

UNION ALL

-- Columns participating in DEFAULT constraints
SELECT
    dc.object_id                                    AS constraint_id,
    c.column_id                                     AS column_id,
    1                                               AS ordinal_position
FROM sys.default_constraints AS dc
INNER JOIN sys.columns AS c
    ON c.object_id = dc.parent_object_id
   AND dc.parent_column_id = c.column_id

UNION ALL

-- Columns participating in FOREIGN KEY constraints
SELECT
    fkc.constraint_object_id                        AS constraint_id,
    fkc.parent_column_id                            AS column_id,
    fkc.constraint_column_id                        AS ordinal_position
FROM sys.foreign_key_columns AS fkc;
