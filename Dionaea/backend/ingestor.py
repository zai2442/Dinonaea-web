import re
import logging
from datetime import datetime
import time
import os
import sys
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.attack_log import AttackLog
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LogIngestor")

# Log format regex
# Example: "Wed, 18 Feb 2026 20:08:41  Username:1 Password:1 ipaddr:127.0.0.1"
# Example 2: "Wed, 18 Feb 2026 20:08:41  Username:1 Password:1 ipaddr:127.0.0.1 Protocol:HTTP"
LOG_PATTERN = re.compile(
    r"(?P<timestamp>[\w]{3}, \d{2} [\w]{3} \d{4} \d{2}:\d{2}:\d{2})\s+"
    r"Username:(?P<username>.*?)\s+"
    r"Password:(?P<password>.*?)\s+"
    r"ipaddr:(?P<ipaddr>.*?)"
    r"(?:\s+Protocol:(?P<protocol>.*))?$"
)

# Date format in log
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S"

class LogHandler(FileSystemEventHandler):
    def __init__(self):
        self.file_offsets = {}

    def on_created(self, event):
        if not event.is_directory and os.path.basename(event.src_path) == "Dionaea.log":
            logger.info(f"New log file detected: {event.src_path}")
            self.process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and os.path.basename(event.src_path) == "Dionaea.log":
            logger.info(f"Log file modified: {event.src_path}")
            self.process_file(event.src_path)

    def process_file(self, filepath):
        if not os.path.exists(filepath):
            return

        offset = self.file_offsets.get(filepath, 0)
        
        try:
            # Check for file truncation/rotation
            current_size = os.path.getsize(filepath)
            if current_size < offset:
                logger.info(f"File {filepath} was truncated or rotated. Resetting offset to 0.")
                offset = 0
            
            with open(filepath, 'r', encoding='utf-8') as f:
                # Seek to last known position
                f.seek(offset)
                lines = f.readlines()
                
                # Update offset
                self.file_offsets[filepath] = f.tell()
                
                if lines:
                    self.ingest_lines(lines)
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")

    def ingest_lines(self, lines):
        db = SessionLocal()
        new_entries = 0
        try:
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                parsed = self.parse_line(line)
                if parsed:
                    # Deduplication check
                    exists = db.query(AttackLog).filter(
                        AttackLog.timestamp == parsed['timestamp'],
                        AttackLog.username == parsed['username'],
                        AttackLog.source_ip == parsed['source_ip']
                    ).first()
                    
                    if exists:
                        continue

                    # Determine Protocol and Port
                    protocol = parsed.get('protocol', 'smb')
                    if not protocol:
                        protocol = 'smb'
                    protocol = protocol.lower()

                    target_port = 445
                    if protocol == 'http':
                        target_port = 80
                    elif protocol == 'smb':
                        target_port = 445
                    
                    # Create record
                    log_entry = AttackLog(
                        timestamp=parsed['timestamp'],
                        username=parsed['username'],
                        password=parsed['password'],
                        source_ip=parsed['source_ip'],
                        target_port=target_port,
                        protocol=protocol,
                        connection_status="attempt",
                        sensor_name="dionaea-node-1",
                        raw_log=line,
                        attack_type=protocol # Mapped from protocol
                    )
                    db.add(log_entry)
                    new_entries += 1
            
            if new_entries > 0:
                db.commit()
                logger.info(f"Ingested {new_entries} new log entries.")
            else:
                logger.debug("No new valid entries found.")
                
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()

    def parse_line(self, line: str):
        match = LOG_PATTERN.search(line)
        if not match:
            return None
        
        data = match.groupdict()
        try:
            dt = datetime.strptime(data['timestamp'], DATE_FORMAT)
            return {
                "timestamp": dt,
                "username": data['username'],
                "password": data['password'],
                "source_ip": data['source_ip'].strip() if 'source_ip' in data else data['ipaddr'].strip(),
                "protocol": data.get('protocol', '').strip() if data.get('protocol') else None
            }
        except ValueError as e:
            logger.error(f"Date parsing error: {e} for line: {line}")
            return None

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

def start_monitoring(path):
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    logger.info(f"Started monitoring {path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    init_db()
    
    # Monitor directory
    MONITOR_DIR = "/tmp"
    
    if not os.path.exists(MONITOR_DIR):
        os.makedirs(MONITOR_DIR)
        logger.info(f"Created directory: {MONITOR_DIR}")
        
    logger.info(f"Starting Log Ingestor Service on {MONITOR_DIR} (filtering for Dionaea.log)...")
    start_monitoring(MONITOR_DIR)
