import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.attack_log import AttackLog
from app.schemas.attack_log import AttackLogFilter
from app.core.config import settings
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AttackLogService:
    def __init__(self, db: Session):
        self.db = db
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def get_logs(self, filters: AttackLogFilter):
        query = self.db.query(AttackLog)

        if filters.start_time:
            query = query.filter(AttackLog.timestamp >= filters.start_time)
        if filters.end_time:
            query = query.filter(AttackLog.timestamp <= filters.end_time)
        if filters.source_ip:
            query = query.filter(AttackLog.source_ip.contains(filters.source_ip))
        if filters.username:
            query = query.filter(AttackLog.username.contains(filters.username))
        if filters.password:
            query = query.filter(AttackLog.password.contains(filters.password))
        if filters.attack_type:
            query = query.filter(AttackLog.attack_type.contains(filters.attack_type))

        total = query.count()
        logs = query.order_by(desc(AttackLog.timestamp)).offset(filters.offset).limit(filters.limit).all()
        
        return logs, total

    def get_statistics(self):
        # Try to get from cache first
        cache_key = "dionaea_stats"
        if self.redis_client:
            cached_stats = self.redis_client.get(cache_key)
            if cached_stats:
                return json.loads(cached_stats)

        # Calculate statistics
        # 1. Top 10 IPs
        top_ips = self.db.query(
            AttackLog.source_ip, func.count(AttackLog.id).label('count')
        ).group_by(AttackLog.source_ip).order_by(desc('count')).limit(10).all()
        
        # 2. Top 5 Usernames
        top_usernames = self.db.query(
            AttackLog.username, func.count(AttackLog.id).label('count')
        ).group_by(AttackLog.username).order_by(desc('count')).limit(5).all()

        # 3. Top 20 Passwords
        top_passwords = self.db.query(
            AttackLog.password, func.count(AttackLog.id).label('count')
        ).group_by(AttackLog.password).order_by(desc('count')).limit(20).all()

        # 4. Total Logs Count
        total_logs = self.db.query(AttackLog).count()

        stats = {
            "top_ips": [{"name": ip, "value": count} for ip, count in top_ips if ip],
            "top_usernames": [{"name": user, "value": count} for user, count in top_usernames if user],
            "top_passwords": [{"name": pwd, "value": count} for pwd, count in top_passwords if pwd],
            "total_logs": total_logs,
            "timestamp": datetime.now().isoformat()
        }

        # Cache for 10 minutes
        if self.redis_client:
            self.redis_client.setex(cache_key, 600, json.dumps(stats))

        return stats

    def get_summary(self):
        # This mimics the output of Login_statistics.sh
        # Most login IP, Username, Password
        
        stats = self.get_statistics()
        
        most_login_ip = stats['top_ips'][0] if stats['top_ips'] else {"name": "N/A", "value": 0}
        most_login_user = stats['top_usernames'][0] if stats['top_usernames'] else {"name": "N/A", "value": 0}
        most_login_pwd = stats['top_passwords'][0] if stats['top_passwords'] else {"name": "N/A", "value": 0}
        
        return {
            "most_login_ip": most_login_ip,
            "most_login_username": most_login_user,
            "most_login_password": most_login_pwd,
            "total_logs": stats.get('total_logs', 0)
        }
    
    def refresh_stats(self):
        # Invalidate cache
        if self.redis_client:
            self.redis_client.delete("dionaea_stats")
        return self.get_statistics()

    def get_traffic_stats(self, filters: AttackLogFilter = None):
        """
        Get traffic analysis statistics:
        1. Attack Type Distribution
        2. Traffic Timeline (Last 24 hours)
        """
        # Base query for Attack Type Distribution
        dist_query = self.db.query(
            AttackLog.attack_type, func.count(AttackLog.id).label('count')
        )
        
        # Base query for Timeline
        timeline_query = self.db.query(
            func.date_trunc('hour', AttackLog.timestamp).label('hour'),
            func.count(AttackLog.id).label('count')
        )

        # Apply Filters if provided
        if filters:
            if filters.start_time:
                dist_query = dist_query.filter(AttackLog.timestamp >= filters.start_time)
                timeline_query = timeline_query.filter(AttackLog.timestamp >= filters.start_time)
            if filters.end_time:
                dist_query = dist_query.filter(AttackLog.timestamp <= filters.end_time)
                timeline_query = timeline_query.filter(AttackLog.timestamp <= filters.end_time)
            if filters.source_ip:
                dist_query = dist_query.filter(AttackLog.source_ip.contains(filters.source_ip))
                timeline_query = timeline_query.filter(AttackLog.source_ip.contains(filters.source_ip))
            if filters.attack_type:
                dist_query = dist_query.filter(AttackLog.attack_type.contains(filters.attack_type))
                timeline_query = timeline_query.filter(AttackLog.attack_type.contains(filters.attack_type))

        # 1. Attack Type Distribution Execution
        attack_types = dist_query.group_by(AttackLog.attack_type).order_by(desc('count')).all()
        
        # 2. Traffic Timeline Execution
        # Default to last 24h if no start time provided for timeline context
        if not filters or not filters.start_time:
            now = datetime.now()
            start_time = now - timedelta(hours=24)
            timeline_query = timeline_query.filter(AttackLog.timestamp >= start_time)
        
        timeline_results = timeline_query.group_by('hour').order_by('hour').all()
         
        return {
            "attack_distribution": [{"name": at, "value": count} for at, count in attack_types if at],
            "timeline": [{"time": t.isoformat(), "count": c} for t, c in timeline_results]
        }
