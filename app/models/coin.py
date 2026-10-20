from datetime import datetime, timezone, date
from app.extensions import db

class CoinEntry(db.Model):
    __tablename__ = 'coin_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False, index=True)
    source = db.Column(db.String(16), default='self', nullable=False, index=True) # 'self' or 'script'
    note = db.Column(db.String(255), nullable=True)
    
    # Snapshot timestamps
    logged_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    # Anti-cheat / Outlier detection
    is_flagged = db.Column(db.Boolean, default=False, nullable=False, index=True)
    flag_reason = db.Column(db.String(255), nullable=True)
    
    # Soft deletion with audit trail
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'source': self.source,
            'note': self.note,
            'logged_at': self.logged_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'is_flagged': self.is_flagged,
            'flag_reason': self.flag_reason,
            'is_deleted': self.is_deleted
        }


class DailySnapshot(db.Model):
    __tablename__ = 'daily_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True) # YYYY-MM-DD
    
    closing_balance = db.Column(db.Integer, nullable=False)
    net_change = db.Column(db.Integer, default=0, nullable=False) # delta vs previous snapshot
    pct_change = db.Column(db.Float, default=0.0, nullable=False)
    rank = db.Column(db.Integer, nullable=True)
    growth_score = db.Column(db.Float, default=0.0, nullable=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uq_user_date_snapshot'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'closing_balance': self.closing_balance,
            'net_change': self.net_change,
            'pct_change': self.pct_change,
            'rank': self.rank,
            'growth_score': self.growth_score
        }
