import secrets
from datetime import datetime, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask_login import UserMixin
from app.extensions import db

ph = PasswordHasher()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile & In-game details
    display_name = db.Column(db.String(64), nullable=True)
    efootball_id = db.Column(db.String(64), nullable=True, index=True)
    bio = db.Column(db.String(300), nullable=True)
    country = db.Column(db.String(4), nullable=True, default='UN') # ISO alpha-2, e.g. 'US', 'GB', 'JP'
    avatar_filename = db.Column(db.String(255), nullable=True)
    
    # Privacy & Status
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    
    # Verification & Tokens
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(100), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    coin_entries = db.relationship('CoinEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    api_tokens = db.relationship('ApiToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    daily_snapshots = db.relationship('DailySnapshot', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    user_badges = db.relationship('UserBadge', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Followers / Following
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str):
        self.password_hash = ph.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False

    @property
    def effective_name(self) -> str:
        return self.display_name if self.display_name else self.username

    @property
    def latest_entry(self):
        from app.models.coin import CoinEntry
        return self.coin_entries.filter_by(is_deleted=False).order_by(CoinEntry.created_at.desc()).first()

    @property
    def current_balance(self) -> int:
        entry = self.latest_entry
        return entry.amount if entry else 0

    @property
    def avatar_url(self) -> str:
        if self.avatar_filename:
            return f"/static/uploads/avatars/{self.avatar_filename}"
        # Fallback generated UI avatar with brand styling
        return f"https://api.dicebear.com/7.x/shapes/svg?seed={self.username}&backgroundColor=0f141c&shapeColor=f5c451,00f084"

    def is_following(self, user) -> bool:
        if user.id is None:
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user) and user.id != self.id:
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)

    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.effective_name,
            'efootball_id': self.efootball_id,
            'bio': self.bio,
            'country': self.country,
            'avatar_url': self.avatar_url,
            'current_balance': self.current_balance,
            'created_at': self.created_at.isoformat()
        }
        if include_private:
            data['email'] = self.email
            data['is_private'] = self.is_private
            data['is_admin'] = self.is_admin
        return data


class ApiToken(db.Model):
    __tablename__ = 'api_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    prefix = db.Column(db.String(16), nullable=False) # e.g. cv_live_ab12
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True) # SHA-256
    revoked = db.Column(db.Boolean, default=False, nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @staticmethod
    def generate_token() -> tuple[str, str, str]:
        """Returns (raw_token, prefix, token_hash)"""
        import hashlib
        raw = f"cv_{secrets.token_urlsafe(32)}"
        prefix = raw[:12]
        token_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        return raw, prefix, token_hash
