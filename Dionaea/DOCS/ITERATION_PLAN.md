# Iteration Plan & Requirement Breakdown

## Sprint 1: User Module (Foundation)
**Goal**: Establish the system foundation with secure user management and RBAC.

### Tasks
- [ ] **Database**: Design and migrate `users`, `roles`, `permissions`, `operation_logs` tables.
- [ ] **Backend**:
    - [ ] Implement JWT Authentication (Login, Refresh, Logout).
    - [ ] Implement Password Recovery flow.
    - [ ] Implement RBAC middleware/dependencies.
    - [ ] Create User CRUD APIs (Register, Update, Delete).
    - [ ] Create Role Management APIs.
    - [ ] Implement Operation Audit Logging.
- [ ] **Frontend**:
    - [ ] Setup Vue 3 + Vite + Pinia + Element Plus project structure.
    - [ ] Develop Login/Register/Forgot Password pages.
    - [ ] Develop User Management table (with pagination/search).
    - [ ] Develop Role Management interface.
- [ ] **Testing**: Unit tests for Auth and User Logic.

## Sprint 2: Honeypot Data Ingestion
**Goal**: Connect to `web_dionaea` logs and establish the data pipeline.

### Tasks
- [ ] **Data Pipeline**:
    - [ ] Develop Log Watcher/Parser service (Python/Filebeat).
    - [ ] Define Log format regex/parsing logic for `web_dionaea`.
    - [ ] Implement "Standardized Storage" logic (Attack Log Model).
- [ ] **Backend**:
    - [ ] Implement WebSocket Manager for real-time pushing.
    - [ ] Create API for querying Attack Logs (filtering by IP, date, etc.).
    - [ ] Implement Attack Type Enumeration logic.
- [ ] **Frontend**:
    - [ ] Develop "Real-time Attack Monitor" view (WebSocket client).
    - [ ] Develop "Attack Log" historical data table.
- [ ] **Testing**: Integration test for Log -> DB -> API flow.

## Sprint 3: Data Visualization
**Goal**: Provide actionable insights through graphical dashboards.

### Tasks
- [ ] **Backend**:
    - [ ] Implement Aggregation APIs (Daily trends, Top IPs, Geo-stats).
    - [ ] Optimize SQL queries for heavy aggregation.
- [ ] **Frontend**:
    - [ ] Integrate ECharts.
    - [ ] Develop "Attack Trend" Line Chart.
    - [ ] Develop "Top Attack Sources" Pie Chart.
    - [ ] Develop "Geographic Distribution" Heatmap.
    - [ ] Develop "Attack Timeline" Gantt Chart.
    - [ ] Create a unified "Dashboard" view combining all charts.
- [ ] **Performance**: Ensure dashboard loads within 2s.

## Sprint 4: System Configuration
**Goal**: Allow dynamic management of honeypot nodes and alerts.

### Tasks
- [ ] **Database**: Create `nodes`, `alert_rules` tables.
- [ ] **Backend**:
    - [ ] Create Node Management APIs (CRUD).
    - [ ] Implement Alerting Engine (Check logs against rules).
- [ ] **Frontend**:
    - [ ] Develop Node Management page.
    - [ ] Develop Alert Rule Configuration page (Thresholds/Keywords).
- [ ] **Testing**: Verify alert triggers on simulated attacks.

## Sprint 5: Security Hardening & Polish
**Goal**: Secure the platform and prepare for delivery.

### Tasks
- [ ] **Security**:
    - [ ] Implement Login Failure Lockout (Redis).
    - [ ] Implement 2FA (TOTP).
- [ ] **Performance**:
    - [ ] Stress test with Locust (1000 users).
    - [ ] Optimize frontend bundle (Split chunks).
- [ ] **DevOps**:
    - [ ] Finalize Docker Compose setup.
    - [ ] Configure GitHub Actions for CI/CD.
    - [ ] Write Deployment & User Manuals.
