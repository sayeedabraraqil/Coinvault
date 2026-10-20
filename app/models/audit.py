import json
from datetime import datetime, timezone
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = db.Column(db.String(50), nullable=False, index=True) # e.g. 'ENTRY_CREATE', 'ENTRY_EDIT', 'ENTRY_DELETE'
    entity_type = db.Column(db.String(50), nullable=False) # e.g. 'CoinEntry', 'User', 'ApiToken'
    entity_id = db.Column(db.Integer, nullable=True)
    old_values = db.Column(db.Text, nullable=True) # JSON serialized
    new_values = db.Column(db.Text, nullable=True) # JSON serialized
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    user = db.relationship('User', foreign_keys=[user_id])

    @staticmethod
    def record(user_id, action, entity_type, entity_id=None, old_val=None, new_val=None, ip=None):
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=json.dumps(old_val, default=str) if old_val is not None else None,
            new_values=json.dumps(new_val, default=str) if new_val is not None else None,
            ip_address=ip
        )
        db.session.add(log)
        return log
