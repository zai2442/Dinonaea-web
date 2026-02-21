-- U1_0__init_rbac_tables.sql

DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS users;
-- Note: We might not want to drop attack_logs if it contained data before. 
-- But for this version, we assume it's part of the new schema or we just revert changes.
-- If we modified attack_logs, we should revert columns.
-- Here we just drop the new tables.
