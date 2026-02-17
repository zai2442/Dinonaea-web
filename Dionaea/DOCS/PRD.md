# Product Requirements Document (PRD)

## 1. Introduction

### 1.1 Purpose
The goal of this project is to perform a secondary development based on the existing `dinoaea-web` honeypot project. The objective is to build a robust Background Management System that provides user permission management and visualization of honeypot capture data. This system will enable administrators to monitor attacks in real-time, analyze historical data, and manage system configurations efficiently.

### 1.2 Scope
The system comprises three main modules:
- **User Management**: Comprehensive RBAC (Role-Based Access Control) system.
- **Honeypot Data Visualization**: Real-time and historical analysis of attack logs.
- **System Configuration**: Management of honeypot nodes and alerting strategies.

The underlying honeypot function (credential harvesting) will continue to use the `web_dionaea` architecture, while the management platform will be a modern web application.

### 1.3 Definitions & Acronyms
- **MVP**: Minimum Viable Product.
- **RBAC**: Role-Based Access Control.
- **TPS**: Transactions Per Second.

## 2. User Roles

| Role | Description |
| :--- | :--- |
| **Super Admin** | Full system access. Can manage users, roles, system configs, and view all data. |
| **Auditor** | View-only access to logs and audit trails. Cannot modify system configs or user data. |
| **Read-Only User** | Basic access to view honeypot data dashboards only. |

## 3. Functional Requirements

### 3.1 User Management
- **Registration & Login**: Secure authentication with JWT. Support for password recovery.
- **Role Management**: Pre-defined roles (Admin, Auditor, User) with granular permission settings.
- **Audit Logs**: Record all critical user actions (login, config changes, data export).

### 3.2 Honeypot Data Analysis
- **Data Ingestion**: Parse logs from `web_dionaea`, normalize data, and store in PostgreSQL.
- **Attack Logs**: Tabular view of attack details (Source IP, Timestamp, Payload, Protocol).
- **Visualization**:
    - Attack Trend (Line Chart).
    - Top Attack Sources (Pie Chart).
    - Geographic Distribution (Heatmap).
    - Attack Timeline (Gantt Chart).
- **Real-time Updates**: WebSocket push for new attack events.

### 3.3 System Configuration
- **Node Management**: Add, remove, update, and query honeypot nodes.
- **Alerting**: Configure thresholds and keyword-based alarms.

## 4. Non-Functional Requirements

### 4.1 Performance
- **Response Time**: Single page data load ≤ 2s.
- **Data Ingestion Latency**: Attack log storage delay ≤ 5s.
- **Concurrency**: Support 1000 concurrent users (Locust stress test).

### 4.2 Availability
- **Uptime**: 99.9% monthly availability.

### 4.3 Security
- **Authentication**: JWT based stateless auth.
- **Protection**: Rate limiting (IP + User dimension).
- **Vulnerability**: 0 High-risk vulnerabilities (OWASP ZAP).

## 5. Success Metrics
- API P99 Latency ≤ 300ms.
- Frontend First Paint ≤ 800KB.
- Test Coverage: Backend ≥ 85%, Frontend ≥ 80%.
