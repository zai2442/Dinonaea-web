from app.models.user import User
from app.models.role import Role, Permission
from app.models.attack_log import AttackLog
from app.models.audit import AuditLog

MODEL_MAPPING = {
    "users": User,
    "roles": Role,
    "permissions": Permission,
    "attack_logs": AttackLog,
    "audit_logs": AuditLog
}

def get_model(resource: str):
    return MODEL_MAPPING.get(resource)
