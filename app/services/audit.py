from app.models.audit import AuditLog

def log_audit(user_id, action, entity_type, entity_id=None, old_val=None, new_val=None, request=None):
    ip = request.remote_addr if request else None
    return AuditLog.record(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_val=old_val,
        new_val=new_val,
        ip=ip
    )
