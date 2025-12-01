-- 06_relational_constraint_info.sql
-- Extracts constraint-level metadata for relational.constraint_info.
-- NOTE: 'table_id' here is the source table object_id from sys.tables.
--       'constraint_id' should be mapped from the constraint's object_id in ETL.

-- CHECK constraints
SELECT
    cc.object_id                                    AS constraint_id,
    cc.parent_object_id                             AS table_id,
    cc.name                                         AS constraint_name,
    'CHECK'                                         AS constraint_type,
    cc.definition                                   AS definition,
    cc.is_disabled                                  AS is_disabled,
    cc.is_not_trusted                               AS is_not_trusted
FROM sys.check_constraints AS cc

UNION ALL

-- DEFAULT constraints
SELECT
    dc.object_id                                    AS constraint_id,
    dc.parent_object_id                             AS table_id,
    dc.name                                         AS constraint_name,
    'DEFAULT'                                       AS constraint_type,
    dc.definition                                   AS definition,
    dc.is_disabled                                  AS is_disabled,
    NULL                                            AS is_not_trusted
FROM sys.default_constraints AS dc

UNION ALL

-- PRIMARY KEY and UNIQUE constraints
SELECT
    kc.object_id                                    AS constraint_id,
    kc.parent_object_id                             AS table_id,
    kc.name                                         AS constraint_name,
    CASE 
        WHEN kc.type = 'PK' THEN 'PRIMARY_KEY'
        WHEN kc.type = 'UQ' THEN 'UNIQUE'
        ELSE 'OTHER'
    END                                             AS constraint_type,
    OBJECT_DEFINITION(kc.object_id)                 AS definition,
    kc.is_disabled                                  AS is_disabled,
    NULL                                            AS is_not_trusted
FROM sys.key_constraints AS kc

UNION ALL

-- FOREIGN KEY constraints
SELECT
    fk.object_id                                    AS constraint_id,
    fk.parent_object_id                             AS table_id,
    fk.name                                         AS constraint_name,
    'FOREIGN_KEY'                                   AS constraint_type,
    OBJECT_DEFINITION(fk.object_id)                 AS definition,
    fk.is_disabled                                  AS is_disabled,
    fk.is_not_trusted                               AS is_not_trusted
FROM sys.foreign_keys AS fk;
