-- 05_relational_column_info.sql
-- Extracts column-level metadata for relational.column_info.
-- NOTE: 'table_id' here is the source table object_id from sys.tables.

SELECT
    c.object_id                                     AS table_id,            -- source table object_id
    c.name                                          AS column_name,
    c.column_id                                     AS ordinal_position,
    typ.name                                        AS data_type,
    c.max_length                                    AS max_length,
    c.precision                                     AS precision,
    c.scale                                         AS scale,
    c.is_nullable                                   AS is_nullable,
    dc.definition                                   AS default_definition,
    cc.definition                                   AS computed_definition,
    c.is_identity                                   AS is_identity,
    ic.seed_value                                   AS identity_seed,
    ic.increment_value                              AS identity_increment,
    c.collation_name                                AS collation_name,
    c.is_sparse                                     AS is_sparse,
    c.is_hidden                                     AS is_hidden,
    c.is_rowguidcol                                 AS is_row_guide_column
FROM sys.columns AS c
INNER JOIN sys.types AS typ
    ON typ.user_type_id = c.user_type_id
LEFT JOIN sys.default_constraints AS dc
    ON dc.parent_object_id = c.object_id
   AND dc.parent_column_id = c.column_id
LEFT JOIN sys.computed_columns AS cc
    ON cc.object_id = c.object_id
   AND cc.column_id = c.column_id
LEFT JOIN sys.identity_columns AS ic
    ON ic.object_id = c.object_id
   AND ic.column_id = c.column_id;
