# Database Changelog

## V1.0 - Init RBAC Tables

**Date:** 2026-02-21
**Author:** Trae AI
**Description:** Initial setup of User, Role, Permission tables and Audit Log.

### Changes
-   **New Tables**:
    -   `users`: Stores user credentials and status.
    -   `roles`: Stores role definitions.
    -   `permissions`: Stores granular permissions.
    -   `user_roles`: Many-to-Many link between User and Role.
    -   `role_permissions`: Many-to-Many link between Role and Permission.
    -   `audit_log`: Logs sensitive actions.
-   **Modified Tables**:
    -   `attack_logs`: Added standard fields (`create_by`, `version`, `deleted`) and indexes.

### Indexes
-   `idx_users_username`: Unique lookup for login.
-   `idx_users_email`: Unique lookup for registration.
-   `idx_attack_logs_timestamp`: Fast time-range queries.
-   `idx_attack_logs_username`: Fast user activity lookup.

### Rollback
-   Run `U1_0__init_rbac_tables.sql` to drop new tables.
-   Note: Data in `users`, `roles`, `permissions` will be lost.

### Performance
-   Expected query time for user login: < 50ms (Indexed username).
-   Expected query time for user list (100k rows): < 200ms (Indexed pagination).
