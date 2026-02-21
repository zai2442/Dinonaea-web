import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import SessionLocal
from app.services.attack_log_service import AttackLogService

def refresh_stats_cache():
    print("Refreshing stats cache...")
    db = SessionLocal()
    try:
        service = AttackLogService(db)
        stats = service.refresh_stats()
        print("Stats refreshed successfully.")
    except Exception as e:
        print(f"Error refreshing stats: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    refresh_stats_cache()
