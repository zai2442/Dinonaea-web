# Changelog

## [Unreleased]

### Added
- **Protocol Recognition**: Added support for SMB and HTTP protocol detection in attack logs.
  - Backend: `ingestor.py` now parses `Protocol:` field and maps ports (HTTP->80, SMB->445). Legacy logs default to SMB.
  - Frontend: Added protocol filter dropdown (SMB/HTTP) to the dashboard log view.
  - Logs: `views.py` now appends `Protocol:HTTP` to web login logs.
- **Statistics**: Added "Total Attack Logs" count to the dashboard (replacing static "Today's Visits").

### Fixed
- **Log Monitoring**: Fixed `ingestor.py` to monitor `/tmp` for `Dionaea.log` specifically (previously monitored a non-existent directory).
- **Log Rotation**: Added handling for file truncation/rotation in `ingestor.py` to prevent data loss or duplication when logs are reset.
- **File Handling**: Fixed `views.py` file mode from invalid `aw` to `a` (append).

### Changed
- **Dashboard**: "Protocol" column in log table now displays protocols in uppercase (e.g., SMB, HTTP).
- **API**: Updated `/api/v1/data/stats/summary` to include `total_logs` count.
