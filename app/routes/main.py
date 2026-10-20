from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from sqlalchemy import desc
from app.extensions import db
from app.models.user import User
from app.models.coin import CoinEntry, DailySnapshot
from app.models.social import Badge
from app.services.analytics import compute_user_analytics, get_global_market_analytics

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Global metrics for landing hero
    market = get_global_market_analytics()

    # Top 3 Richest for Podium preview
    users = User.query.filter_by(is_banned=False, is_private=False).all()
    user_balances = [(u, u.current_balance) for u in users if u.current_balance > 0]
    user_balances.sort(key=lambda x: x[1], reverse=True)
    podium = user_balances[:3]

    # Recent active feed snapshots
    recent_entries = CoinEntry.query.join(User)\
        .filter(CoinEntry.is_deleted == False, User.is_banned == False, User.is_private == False)\
        .order_by(CoinEntry.created_at.desc()).limit(8).all()

    return render_template(
        'index.html',
        market=market,
        podium=podium,
        recent_entries=recent_entries
    )

@main_bp.route('/leaderboards')
def leaderboards():
    metric = request.args.get('metric', 'richest') # richest, fastest_24h, fastest_7d, fastest_30d, streak, consistency, drops, rising
    country = request.args.get('country', 'ALL')
    verified_only = request.args.get('verified', '0') == '1'
    search_q = request.args.get('q', '').strip().lower()

    # Query all valid candidate users
    query = User.query.filter_by(is_banned=False, is_private=False)
    if country != 'ALL':
        query = query.filter_by(country=country)
    if search_q:
        query = query.filter((User.username.ilike(f"%{search_q}%")) | (User.display_name.ilike(f"%{search_q}%")))

    users = query.all()
    rows = []

    now = datetime.now(timezone.utc)
    t_24h = now - timedelta(hours=24)
    t_7d = now - timedelta(days=7)
    t_30d = now - timedelta(days=30)

    def to_utc(dt):
        if dt is None:
            return None
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

    for u in users:
        entries = u.coin_entries.filter_by(is_deleted=False).order_by(CoinEntry.logged_at.asc()).all()
        if not entries:
            continue

        # If verified only is checked, user must have at least one script entry
        has_script = any(e.source == 'script' for e in entries)
        if verified_only and not has_script:
            continue

        latest = entries[-1]
        current_bal = latest.amount

        # Calculate time-window deltas
        b_24h = next((e.amount for e in reversed(entries) if to_utc(e.logged_at) <= t_24h), entries[0].amount)
        b_7d = next((e.amount for e in reversed(entries) if to_utc(e.logged_at) <= t_7d), entries[0].amount)
        b_30d = next((e.amount for e in reversed(entries) if to_utc(e.logged_at) <= t_30d), entries[0].amount)

        gain_24h = current_bal - b_24h
        pct_24h = round((gain_24h / b_24h * 100), 2) if b_24h > 0 else 0.0

        gain_7d = current_bal - b_7d
        pct_7d = round((gain_7d / b_7d * 100), 2) if b_7d > 0 else 0.0

        gain_30d = current_bal - b_30d
        pct_30d = round((gain_30d / b_30d * 100), 2) if b_30d > 0 else 0.0

        # Calculate streaks & volatility
        daily_map = {}
        for e in entries:
            daily_map[e.logged_at.date()] = e.amount
        sorted_dates = sorted(daily_map.keys())
        daily_changes = [daily_map[sorted_dates[i]] - daily_map[sorted_dates[i-1]] for i in range(1, len(sorted_dates))]

        streak = 0
        for c in reversed(daily_changes):
            if c > 0:
                streak += 1
            elif c == 0:
                continue
            else:
                break

        highest_single_day = max(daily_changes) if daily_changes else 0
        biggest_single_drop = min(daily_changes) if daily_changes else 0

        # Sparkline points (last 10)
        sparkline = [e.amount for e in entries[-10:]]

        # Is flagged recently
        is_flagged = any(e.is_flagged for e in entries[-3:])

        rows.append({
            'user': u,
            'current_balance': current_bal,
            'gain_24h': gain_24h,
            'pct_24h': pct_24h,
            'gain_7d': gain_7d,
            'pct_7d': pct_7d,
            'gain_30d': gain_30d,
            'pct_30d': pct_30d,
            'streak': streak,
            'highest_day': highest_single_day,
            'biggest_drop': biggest_single_drop,
            'sparkline': sparkline,
            'is_verified': has_script,
            'is_flagged': is_flagged,
            'entry_count': len(entries),
            'latest_update': latest.logged_at.strftime('%Y-%m-%d %H:%M')
        })

    # Sort based on selected metric
    if metric == 'richest':
        rows.sort(key=lambda x: x['current_balance'], reverse=True)
    elif metric == 'fastest_24h':
        # Exclude flagged from fastest growing
        rows = [r for r in rows if not r['is_flagged']]
        rows.sort(key=lambda x: x['gain_24h'], reverse=True)
    elif metric == 'fastest_7d':
        rows = [r for r in rows if not r['is_flagged']]
        rows.sort(key=lambda x: x['gain_7d'], reverse=True)
    elif metric == 'fastest_30d':
        rows = [r for r in rows if not r['is_flagged']]
        rows.sort(key=lambda x: x['gain_30d'], reverse=True)
    elif metric == 'single_day':
        rows = [r for r in rows if not r['is_flagged']]
        rows.sort(key=lambda x: x['highest_day'], reverse=True)
    elif metric == 'streak':
        rows.sort(key=lambda x: x['streak'], reverse=True)
    elif metric == 'drops':
        rows.sort(key=lambda x: x['biggest_drop']) # most negative first
    elif metric == 'rising':
        # Steepest climb for newer users (registered within last 14 days)
        rows.sort(key=lambda x: x['pct_7d'], reverse=True)
    else:
        rows.sort(key=lambda x: x['current_balance'], reverse=True)

    # Assign ranks
    for idx, r in enumerate(rows, start=1):
        r['rank'] = idx

    return render_template(
        'leaderboards/index.html',
        rows=rows,
        metric=metric,
        country=country,
        verified_only=verified_only,
        search_q=search_q,
        total_players=len(rows)
    )

@main_bp.route('/analytics')
def analytics():
    market = get_global_market_analytics()
    all_users = User.query.filter_by(is_banned=False, is_private=False).all()
    user_scores = []
    for u in all_users:
        stats = compute_user_analytics(u.id)
        if stats and stats['current_balance'] > 0:
            user_scores.append({
                'username': u.username,
                'display_name': u.effective_name,
                'avatar_url': u.avatar_url,
                'balance': stats['current_balance'],
                'growth_score': stats['growth_score'],
                'streak': stats['streak_days']
            })
    user_scores.sort(key=lambda x: x['growth_score'], reverse=True)

    return render_template('analytics/index.html', market=market, top_scores=user_scores[:10])

@main_bp.route('/compare')
def compare():
    u1_name = request.args.get('u1', '').strip().lower()
    u2_name = request.args.get('u2', '').strip().lower()

    all_users = User.query.filter_by(is_banned=False, is_private=False).order_by(User.username.asc()).all()

    user1 = None
    user2 = None
    stats1 = None
    stats2 = None

    if u1_name:
        user1 = User.query.filter_by(username=u1_name, is_banned=False).first()
        if user1:
            stats1 = compute_user_analytics(user1.id)

    if u2_name:
        user2 = User.query.filter_by(username=u2_name, is_banned=False).first()
        if user2:
            stats2 = compute_user_analytics(user2.id)

    # If no users chosen and current_user is authenticated, pick current_user as u1 and top ranked as u2
    if not user1 and current_user.is_authenticated:
        user1 = current_user
        stats1 = compute_user_analytics(user1.id)
    if not user2 and all_users:
        # find someone other than user1
        other = next((u for u in all_users if user1 and u.id != user1.id), None)
        if other:
            user2 = other
            stats2 = compute_user_analytics(user2.id)

    return render_template(
        'compare/index.html',
        all_users=all_users,
        user1=user1,
        user2=user2,
        stats1=stats1,
        stats2=stats2
    )

@main_bp.route('/achievements')
def achievements():
    badges = Badge.query.order_by(Badge.tier.asc()).all()
    unlocked_slugs = set()
    if current_user.is_authenticated:
        unlocked = current_user.user_badges.all()
        unlocked_slugs = {ub.badge.slug for ub in unlocked}

    return render_template('achievements/index.html', badges=badges, unlocked_slugs=unlocked_slugs)

@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
