# Traffic Analysis Page Development Guide

## Overview
This document outlines the development plan and progress for the Traffic Analysis Page. The goal is to provide real-time traffic analysis, regex-based filtering, and attack tagging.

## Features
1.  **Regex Engine**: Load rules from `/home/kali/Dionaea/Dinonaea-web/Dionaea/reg.txt`.
2.  **Traffic Capture**: Process `Dionaea.log` via `ingestor.py`.
3.  **Filtering & Tagging**: Match logs against regex rules and tag them with `attack_type`.
4.  **Visualization**: Dashboard with stats and charts.
5.  **Logging**: Record analysis process.

## Architecture
-   **Backend**: Python (FastAPI) + `watchdog` for log ingestion.
-   **Frontend**: HTML/JS + Tailwind CSS + ECharts.
-   **Database**: PostgreSQL (`attack_logs` table).

## Development Steps

### Phase 1: Backend & Core Logic
- [ ] Create `backend/app/core/rules.py` to parse `reg.txt`.
- [ ] Update `backend/ingestor.py` to integrate the rule engine.
- [ ] Verify `AttackLog` model supports `attack_type`.
- [ ] Add unit tests for regex matching.

### Phase 2: Frontend Implementation
- [ ] Update `dashboard.html` to include "Traffic Analysis" view.
- [ ] Update `dashboard.js` to handle navigation and data fetching.
- [ ] Implement charts and tables for the new view.

### Phase 3: Testing & Validation
- [ ] Verify real-time tagging.
- [ ] Check visualization correctness.
- [ ] Stress test with large logs.

## Rule Format
The `reg.txt` file contains categories and regex rules.
-   Categories: ID -> Name
-   Rules: ID -> Regex
The parser distinguishes them by checking if the content looks like a regex.

## Progress
- **2026-02-22**: Initial design and documentation created.
