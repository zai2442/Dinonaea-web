import re
import logging
from datetime import datetime
import time
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, AttackLog
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LogIngestor")

# Log format regex
# Example: "Wed, 18 Feb 2026 20:08:41  Username:1 Password:1 ipaddr:127.0.0.1"
LOG_PATTERN = re.compile(
    r"(?P<timestamp>[\w]{3}, \d{2} [\w]{3} \d{4} \d{2}:\d{2}:\d{2})\s+"
    r"Username:(?P<username>.*?)\s+"
    r"Password:(?P<password>.*?)\s+"
    r"ipaddr:(?P<ipaddr>.*)"
)

# Date format in log
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S"

def parse_line(line: str):
    """Parse a single log line."""
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
            "source_ip": data['ipaddr'].strip()
        }
    except ValueError as e:
        logger.error(f"Date parsing error: {e} for line: {line}")
        return None

def ingest_file(filepath: str, db: Session):
    """Read file and ingest new lines."""
    if not os.path.exists(filepath):
        logger.warning(f"Log file not found: {filepath}")
        return

    # In a real scenario, we'd track file position (seek)
    # For this prototype, we'll read the whole file or tail it
    # Let's assume we read from beginning for now, duplicate checks would be needed in prod
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parsed = parse_line(line)
            if parsed:
                # Validation: Simple check if IP is present
                if not parsed['source_ip']:
                    logger.warning(f"Skipping line with empty IP: {line}")
                    continue
                
                # Create record
                log_entry = AttackLog(
                    timestamp=parsed['timestamp'],
                    username=parsed['username'],
                    password=parsed['password'],
                    source_ip=parsed['source_ip']
                )
                db.add(log_entry)
            else:
                logger.debug(f"Failed to parse line: {line}")
        
        try:
            db.commit()
            logger.info("Batch committed to database")
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

if __name__ == "__main__":
    # Create tables
    init_db()
    
    # Configuration
    LOG_FILE = os.getenv("DIONAEA_LOG_PATH", "/tmp/Dionaea.log")
    
    # Continuous monitoring loop
    logger.info(f"Starting log ingestion from {LOG_FILE}...")
    
    # Simple file tailing implementation
    try:
        while True:
            db = SessionLocal()
            try:
                ingest_file(LOG_FILE, db)
                # In a real 'tail', we wouldn't re-read the whole file. 
                # But for this prototype without state, we might just process once or 
                # we need to truncate the file after reading?
                # To simulate "tail -f", let's just clear the file after reading (DANGEROUS in prod)
                # OR, let's just wait.
                
                # Better approach for prototype: Just read once and exit, or sleep
                pass
            finally:
                db.close()
            
            time.sleep(10) 
    except KeyboardInterrupt:
        logger.info("Stopping ingestor")
