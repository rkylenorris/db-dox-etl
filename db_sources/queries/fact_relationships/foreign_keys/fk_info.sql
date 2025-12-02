-- 08_relational_foreign_key.sql
-- Extracts foreign key-level metadata for relational.foreign_key.
-- NOTE: 'foreign_key_id' and 'constraint_id' here both use the FK object's object_id.
--       'referenced_table_id' is the referenced table's object_id.

SELECT
    fk.object_id                                    AS foreign_key_id,
    fk.object_id                                    AS constraint_id,
    fk.referenced_object_id                         AS referenced_table_id,
    fk.update_referential_action_desc               AS on_update_action,
    fk.delete_referential_action_desc               AS on_delete_action,
    fk.is_disabled                                  AS is_disabled,
    fk.is_not_trusted                               AS is_not_trusted
FROM sys.foreign_keys AS fk;
