import re
import logging
from datetime import datetime
import time
import os
import sys
import socket
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.attack_log import AttackLog
from app.models.node import Node
from app.core.rules import RuleEngine
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LogIngestor")

# Log format regex
# Flexible pattern to capture ALL traffic
# It will first capture timestamp and the rest of the message
# Then we try to extract structured data from the message
LOG_PATTERN = re.compile(
    r"(?P<timestamp>[\w]{3}, \d{2} [\w]{3} \d{4} \d{2}:\d{2}:\d{2})\s+(?P<content>.*)$"
)

# Sub-patterns for structured data
USERNAME_PATTERN = re.compile(r"Username:(?P<username>.*?)(?:\s+|$)")
PASSWORD_PATTERN = re.compile(r"Password:(?P<password>.*?)(?:\s+|$)")
IPADDR_PATTERN = re.compile(r"ipaddr:(?P<ipaddr>.*?)(?:\s+|$)")
PROTOCOL_PATTERN = re.compile(r"Protocol:(?P<protocol>.*?)(?:\s+|$)")
PORT_PATTERN = re.compile(r"Port:(?P<port>\d+)(?:\s+|$)")
HTTP_NOT_FOUND_PATTERN = re.compile(r"Not Found:\s+(?P<path>.*)$")

# Initialize Rule Engine
REG_FILE_PATH = "/home/kali/Dionaea/Dinonaea-web/Dionaea/reg.txt"
rule_engine = RuleEngine(REG_FILE_PATH)

# Date format in log
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class LogHandler(FileSystemEventHandler):
    def __init__(self):
        self.file_offsets = {}
        # Allow override via environment variable
        self.env_sensor_name = os.environ.get("DIONAEA_SENSOR_NAME")
        if self.env_sensor_name:
            logger.info(f"Using sensor name from environment: {self.env_sensor_name}")

    def _get_sensor_name(self, db, ip, port=None):
        if self.env_sensor_name:
            return self.env_sensor_name
            
        try:
            logger.debug(f"Resolving sensor name for IP: {ip}, Port: {port}")
            query = db.query(Node).filter(Node.ip_address == ip)
            if port:
                # Try specific port match first
                node = query.filter(Node.port == port).first()
                if node:
                    return node.name
            
            # Fallback to first node for this IP
            node = query.first()
            if node:
                return node.name
            
            # Create if not exists (defaulting to port 80 if not provided)
            new_node = Node(
                name=f"Dionaea-Node-{ip}",
                ip_address=ip,
                port=port if port else 80,
                status="online",
                description="Auto-created by ingestor",
                is_active=True
            )
            db.add(new_node)
            db.commit()
            db.refresh(new_node)
            logger.info(f"Created new node for local IP: {ip}, Port: {new_node.port}")
            return new_node.name
        except Exception as e:
            logger.error(f"Error resolving sensor name: {e}")
            return "unknown-sensor"

    def _get_local_ip(self):
        if not hasattr(self, '_local_ip'):
            self._local_ip = get_local_ip()
        return self._local_ip

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
            with open(filepath, 'r', encoding='utf-8') as f:
                f.seek(offset)
                lines = f.readlines()
                if lines:
                    self.ingest_lines(lines)
                    self.file_offsets[filepath] = f.tell()
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")

    def get_cached_sensor_name(self, db, ip, port):
        if not hasattr(self, '_sensor_cache'):
            self._sensor_cache = {}
        
        key = (ip, port)
        if key not in self._sensor_cache:
            self._sensor_cache[key] = self._get_sensor_name(db, ip, port)
        
        return self._sensor_cache[key]

    def ingest_lines(self, lines):
        db = SessionLocal()
        new_entries = 0
        local_ip = self._get_local_ip()
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
                        AttackLog.source_ip == parsed['source_ip'],
                        AttackLog.raw_log == line
                    ).first()
                    
                    if exists:
                        continue

                    # Determine Protocol and Port
                    protocol = parsed.get('protocol', 'smb')
                    if not protocol:
                        protocol = 'smb'
                    protocol = protocol.lower()

                    # Use parsed target_port if available, otherwise fallback
                    target_port = parsed.get('target_port')
                    if not target_port:
                        if protocol == 'http':
                            target_port = 80
                        elif protocol == 'smb':
                            target_port = 445
                        else:
                            target_port = 80 # default
                    
                    # Resolve sensor name based on IP and Port
                    sensor_name = self.get_cached_sensor_name(db, local_ip, target_port)

                    # Match against regex rules
                    matched_category = rule_engine.match(line)
                    attack_type = matched_category if matched_category else protocol

                    # Modify raw_log if it contains "Not Found" for consistent display
                    raw_log = line
                    if "Not Found:" in raw_log:
                        raw_log = raw_log.replace("Not Found:", f"{protocol.upper()}:")

                    # Create record
                    log_entry = AttackLog(
                        timestamp=parsed['timestamp'],
                        username=parsed['username'],
                        password=parsed['password'],
                        source_ip=parsed['source_ip'],
                        target_port=target_port,
                        protocol=protocol,
                        connection_status="attempt",
                        sensor_name=sensor_name,
                        raw_log=raw_log,
                        attack_type=attack_type # Mapped from regex or protocol
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
        content = data['content']
        
        try:
            dt = datetime.strptime(data['timestamp'], DATE_FORMAT)
            
            # Default values
            username = "-"
            password = "-"
            source_ip = "unknown"
            protocol = "smb"
            
            # Try to extract structured fields
            u_match = USERNAME_PATTERN.search(content)
            p_match = PASSWORD_PATTERN.search(content)
            i_match = IPADDR_PATTERN.search(content)
            pr_match = PROTOCOL_PATTERN.search(content)
            port_match = PORT_PATTERN.search(content)
            
            if u_match: username = u_match.group('username')
            if p_match: password = p_match.group('password')
            if i_match: source_ip = i_match.group('ipaddr').strip()
            if pr_match: protocol = pr_match.group('protocol').strip()
            
            target_port = None
            if port_match:
                try:
                    target_port = int(port_match.group('port'))
                except ValueError:
                    pass

            # Fallback for "Not Found" logs
            if username == "-" and "Not Found:" in content:
                nf_match = HTTP_NOT_FOUND_PATTERN.search(content)
                if nf_match:
                    protocol = "http"
                    username = protocol.upper()
                    password = nf_match.group('path')

            # Generic fallback for any other info
            if username == "-" and password == "-":
                username = protocol.upper()
                password = content[:255] # Limit length

            return {
                "timestamp": dt,
                "username": username,
                "password": password,
                "source_ip": source_ip,
                "protocol": protocol,
                "target_port": target_port
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
    
    # Process existing log file immediately on start
    log_file = os.path.join(path, "Dionaea.log")
    if os.path.exists(log_file):
        logger.info(f"Processing existing log file: {log_file}")
        event_handler.process_file(log_file)
        
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
