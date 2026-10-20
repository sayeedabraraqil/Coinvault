from datetime import datetime, timezone
from app.extensions import db

class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='uq_follower_followed'),
    )


class Badge(db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(32), default='general', nullable=False) # 'streak', 'milestone', 'growth', 'special'
    tier = db.Column(db.String(20), default='bronze', nullable=False) # 'bronze', 'silver', 'gold', 'diamond'
    icon_name = db.Column(db.String(50), nullable=False) # SVG icon reference name

    user_badges = db.relationship('UserBadge', backref='badge', lazy='dynamic', cascade='all, delete-orphan')


class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False, index=True)
    awarded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),
    )


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reported_entry_id = db.Column(db.Integer, db.ForeignKey('coin_entries.id', ondelete='CASCADE'), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False) # 'pending', 'resolved', 'dismissed'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    reporter = db.relationship('User', foreign_keys=[reporter_id])
    entry = db.relationship('CoinEntry', foreign_keys=[reported_entry_id])
