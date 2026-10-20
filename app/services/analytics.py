import math
from datetime import datetime, timezone, timedelta, date
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.coin import CoinEntry, DailySnapshot

def compute_user_analytics(user_id: int):
    """
    Computes comprehensive analytics and indicators for a given user.
    """
    user = db.session.get(User, user_id)
    if not user:
        return None

    # Fetch ordered active entries
    entries = CoinEntry.query.filter_by(user_id=user_id, is_deleted=False)\
        .order_by(CoinEntry.logged_at.asc()).all()

    if not entries:
        return {
            'current_balance': 0,
            'net_change_24h': 0,
            'pct_change_24h': 0.0,
            'net_change_7d': 0,
            'pct_change_7d': 0.0,
            'net_change_30d': 0,
            'pct_change_30d': 0.0,
            'avg_daily_gain': 0,
            'volatility': 0.0,
            'best_day': 0,
            'worst_day': 0,
            'streak_days': 0,
            'growth_score': 0.0,
            'projected_7d': 0,
            'projected_30d': 0,
            'percentile': 0.0,
            'rank': None,
            'sparkline': [],
            'history': []
        }

    now = datetime.now(timezone.utc)
    current_balance = entries[-1].amount

    def to_utc(dt):
        if dt is None:
            return None
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

    # Window deltas: find baseline closest to 24h, 7d, 30d ago
    t_24h = now - timedelta(hours=24)
    t_7d = now - timedelta(days=7)
    t_30d = now - timedelta(days=30)

    b_24h = next((e.amount for e in reversed(entries) if to_utc(e.logged_at) <= t_24h), entries[0].amount)
    b_7d = next((e.amount for e in reversed(entries) if to_utc(e.logged_at) <= t_7d), entries[0].amount)
    b_30d = next((e.amount for e in reversed(entries) if to_utc(e.logged_at) <= t_30d), entries[0].amount)

    net_24h = current_balance - b_24h
    pct_24h = round((net_24h / b_24h * 100), 2) if b_24h > 0 else 0.0

    net_7d = current_balance - b_7d
    pct_7d = round((net_7d / b_7d * 100), 2) if b_7d > 0 else 0.0

    net_30d = current_balance - b_30d
    pct_30d = round((net_30d / b_30d * 100), 2) if b_30d > 0 else 0.0

    # Group entries by date to find daily net deltas
    daily_map = {}
    for e in entries:
        d = e.logged_at.date()
        daily_map[d] = e.amount # last recorded balance on that day

    sorted_dates = sorted(daily_map.keys())
    daily_changes = []
    for i in range(1, len(sorted_dates)):
        change = daily_map[sorted_dates[i]] - daily_map[sorted_dates[i-1]]
        daily_changes.append(change)

    best_day = max(daily_changes) if daily_changes else 0
    worst_day = min(daily_changes) if daily_changes else 0
    avg_daily_gain = int(sum(daily_changes) / len(daily_changes)) if daily_changes else 0

    # Volatility (Standard Deviation of daily changes)
    if len(daily_changes) > 1:
        mean_c = sum(daily_changes) / len(daily_changes)
        variance = sum((x - mean_c) ** 2 for x in daily_changes) / (len(daily_changes) - 1)
        volatility = round(math.sqrt(variance), 2)
    else:
        volatility = 0.0

    # Consecutive streak of positive growth
    streak = 0
    for change in reversed(daily_changes):
        if change > 0:
            streak += 1
        elif change == 0:
            continue
        else:
            break

    # Transparent Growth Score Formula:
    # Growth Score = (30d % Growth * 0.40) + (Consistency Factor * 0.35) + (Streak Bonus * 0.25)
    # Scaled 0 to 100
    growth_component = min(100.0, max(0.0, pct_30d))
    if volatility == 0:
        consistency_component = 90.0 if avg_daily_gain > 0 else 50.0
    else:
        # Lower volatility relative to gain gives higher consistency
        rel_vol = volatility / (abs(avg_daily_gain) + 100)
        consistency_component = max(0.0, min(100.0, 100.0 - (rel_vol * 35.0)))
    streak_component = min(100.0, streak * 10.0)

    growth_score = round((growth_component * 0.40) + (consistency_component * 0.35) + (streak_component * 0.25), 1)

    # Projections (Linear + EMA trend)
    daily_trend = max(0, avg_daily_gain)
    projected_7d = current_balance + int(daily_trend * 7)
    projected_30d = current_balance + int(daily_trend * 30)

    # Sparkline (last 14 points)
    sparkline = [e.amount for e in entries[-14:]]

    # Global Rank and Percentile calculation
    # Subquery: highest active balance per non-private, non-banned user
    all_users = User.query.filter_by(is_banned=False, is_private=False).all()
    user_balances = [(u.id, u.current_balance) for u in all_users]
    user_balances.sort(key=lambda x: x[1], reverse=True)

    rank = None
    percentile = 0.0
    total_tracked = len(user_balances)
    if total_tracked > 0:
        for idx, (uid, bal) in enumerate(user_balances, start=1):
            if uid == user_id:
                rank = idx
                percentile = round(((total_tracked - idx + 1) / total_tracked) * 100, 1)
                break

    return {
        'current_balance': current_balance,
        'net_change_24h': net_24h,
        'pct_change_24h': pct_24h,
        'net_change_7d': net_7d,
        'pct_change_7d': pct_7d,
        'net_change_30d': net_30d,
        'pct_change_30d': pct_30d,
        'avg_daily_gain': avg_daily_gain,
        'volatility': volatility,
        'best_day': best_day,
        'worst_day': worst_day,
        'streak_days': streak,
        'growth_score': growth_score,
        'projected_7d': projected_7d,
        'projected_30d': projected_30d,
        'percentile': percentile,
        'rank': rank,
        'sparkline': sparkline,
        'history': [{'amount': e.amount, 'logged_at': e.logged_at.strftime('%Y-%m-%d %H:%M'), 'source': e.source, 'note': e.note, 'is_flagged': e.is_flagged} for e in entries]
    }

def get_global_market_analytics():
    """
    Computes platform-wide global metrics: total coins tracked, active users,
    median balance, distribution histogram buckets, top daily movers, gainers vs losers.
    """
    users = User.query.filter_by(is_banned=False, is_private=False).all()
    balances = [u.current_balance for u in users if u.current_balance > 0]
    balances.sort()

    total_coins = sum(balances)
    user_count = len(users)
    active_count = len(balances)

    median_balance = 0
    if balances:
        mid = len(balances) // 2
        median_balance = (balances[mid] if len(balances) % 2 != 0 else int((balances[mid-1] + balances[mid]) / 2))

    # Distribution histogram (6 logarithmic / tiered brackets)
    brackets = [
        {'label': '0 - 1K', 'min': 0, 'max': 1000, 'count': 0},
        {'label': '1K - 5K', 'min': 1001, 'max': 5000, 'count': 0},
        {'label': '5K - 20K', 'min': 5001, 'max': 20000, 'count': 0},
        {'label': '20K - 50K', 'min': 20001, 'max': 50000, 'count': 0},
        {'label': '50K - 100K', 'min': 50001, 'max': 100000, 'count': 0},
        {'label': '100K+', 'min': 100001, 'max': float('inf'), 'count': 0},
    ]

    for b in balances:
        for br in brackets:
            if br['min'] <= b <= br['max']:
                br['count'] += 1
                break

    # Gainers vs Losers in last 24h
    gainers = 0
    losers = 0
    neutral = 0
    for u in users:
        latest = u.coin_entries.filter_by(is_deleted=False).order_by(CoinEntry.logged_at.desc()).limit(2).all()
        if len(latest) >= 2:
            d = latest[0].amount - latest[1].amount
            if d > 0:
                gainers += 1
            elif d < 0:
                losers += 1
            else:
                neutral += 1
        elif len(latest) == 1:
            gainers += 1

    return {
        'total_coins': total_coins,
        'user_count': user_count,
        'active_count': active_count,
        'median_balance': median_balance,
        'brackets': brackets,
        'gainers': gainers,
        'losers': losers,
        'neutral': neutral
    }
