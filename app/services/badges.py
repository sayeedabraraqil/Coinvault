from datetime import datetime, timezone
from app.extensions import db
from app.models.social import Badge, UserBadge
from app.models.coin import CoinEntry

INITIAL_BADGES = [
    {
        'slug': 'genesis_log',
        'title': 'The First Reserve',
        'description': 'Logged your first eFootball coin balance on COINVAULT.',
        'category': 'milestone',
        'tier': 'bronze',
        'icon_name': 'coin'
    },
    {
        'slug': 'streak_7',
        'title': 'Tactical Discipline',
        'description': 'Maintained a 7-day positive coin logging streak.',
        'category': 'streak',
        'tier': 'silver',
        'icon_name': 'flame'
    },
    {
        'slug': 'centurion_10k',
        'title': 'Division 1 Reserves',
        'description': 'Surpassed a total vault balance of 10,000 coins.',
        'category': 'milestone',
        'tier': 'silver',
        'icon_name': 'shield'
    },
    {
        'slug': 'high_roller_50k',
        'title': 'Club President',
        'description': 'Accumulated over 50,000 active eFootball coins.',
        'category': 'milestone',
        'tier': 'gold',
        'icon_name': 'crown'
    },
    {
        'slug': 'whale_100k',
        'title': 'Galáctico Vault',
        'description': 'Breached the 100,000 elite coin sovereign tier.',
        'category': 'milestone',
        'tier': 'diamond',
        'icon_name': 'gem'
    },
    {
        'slug': 'growth_10pct',
        'title': 'Market Outperformer',
        'description': 'Achieved >10% coin growth over a rolling 7-day period.',
        'category': 'growth',
        'tier': 'gold',
        'icon_name': 'trending-up'
    },
    {
        'slug': 'verified_source',
        'title': 'Direct Terminal Link',
        'description': 'Verified balance via official Tampermonkey companion userscript.',
        'category': 'special',
        'tier': 'diamond',
        'icon_name': 'check-circle'
    },
    {
        'slug': 'top_10_elite',
        'title': 'Podium Contender',
        'description': 'Secured a top 10 position on the global wealth leaderboard.',
        'category': 'special',
        'tier': 'diamond',
        'icon_name': 'trophy'
    }
]

def init_default_badges():
    """Ensure all default badges exist in the database."""
    for b in INITIAL_BADGES:
        existing = Badge.query.filter_by(slug=b['slug']).first()
        if not existing:
            badge = Badge(**b)
            db.session.add(badge)
    db.session.commit()

def award_badge_if_earned(user, badge_slug: str):
    badge = Badge.query.filter_by(slug=badge_slug).first()
    if not badge:
        return False
    already_has = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
    if not already_has:
        ub = UserBadge(user_id=user.id, badge_id=badge.id)
        db.session.add(ub)
        db.session.commit()
        return True
    return False

def check_and_award_user_badges(user):
    """
    Checks all badge criteria for a given user and awards any earned badges.
    """
    entries = user.coin_entries.filter_by(is_deleted=False).order_by(CoinEntry.logged_at.asc()).all()
    if not entries:
        return

    # 1. Genesis Log
    award_badge_if_earned(user, 'genesis_log')

    current_balance = entries[-1].amount

    # 2. Balance Milestones
    if current_balance >= 10_000:
        award_badge_if_earned(user, 'centurion_10k')
    if current_balance >= 50_000:
        award_badge_if_earned(user, 'high_roller_50k')
    if current_balance >= 100_000:
        award_badge_if_earned(user, 'whale_100k')

    # 3. Verified Script Source
    has_script_entry = any(e.source == 'script' for e in entries)
    if has_script_entry:
        award_badge_if_earned(user, 'verified_source')
