-- V1_0__init_rbac_tables.sql

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    create_by INTEGER,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_by INTEGER,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- 2. Create Roles Table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    create_by INTEGER,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_by INTEGER,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_roles_code ON roles(code);

-- 3. Create Permissions Table
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    resource_type VARCHAR(255),
    create_by INTEGER,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_by INTEGER,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_permissions_code ON permissions(code);

-- 4. Create User_Roles Table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- 5. Create Role_Permissions Table
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- 6. Create Audit_Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(255) NOT NULL,
    resource_id VARCHAR(255),
    params JSONB,
    result VARCHAR(255),
    ip_address VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by INTEGER,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_by INTEGER,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- 7. Modify Existing Attack_Logs Table (if exists, or create new)
-- Assuming attack_logs exists from previous version, we alter it.
-- If not, create it.
CREATE TABLE IF NOT EXISTS attack_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    username VARCHAR(255),
    password VARCHAR(255),
    source_ip VARCHAR(255),
    protocol VARCHAR(50),
    sensor_name VARCHAR(100),
    create_by INTEGER,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_by INTEGER,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    deleted BOOLEAN DEFAULT FALSE
);

-- Add indexes for attack_logs
CREATE INDEX IF NOT EXISTS idx_attack_logs_timestamp ON attack_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_attack_logs_username ON attack_logs(username);
CREATE INDEX IF NOT EXISTS idx_attack_logs_source_ip ON attack_logs(source_ip);
CREATE INDEX IF NOT EXISTS idx_attack_log_time_user_ip ON attack_logs(timestamp, username, source_ip);
