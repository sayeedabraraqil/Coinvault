import math
from datetime import datetime, timezone, timedelta
from app.models.coin import CoinEntry

def evaluate_entry_for_outliers(user, new_amount: int, logged_at: datetime, source: str) -> tuple[bool, str | None]:
    """
    Evaluates whether a new coin entry is statistically anomalous.
    Returns (is_flagged, flag_reason).
    """
    # 1. Absolute sanity ceiling (eFootball max realistic coin threshold)
    if new_amount > 20_000_000:
        return True, f"Balance {new_amount:,} exceeds realistic platform ceiling of 20,000,000 coins."

    # 2. Compare against user's history
    history = CoinEntry.query.filter_by(user_id=user.id, is_deleted=False)\
        .order_by(CoinEntry.created_at.desc()).limit(30).all()

    if not history:
        # First entry: If a brand-new unverified user starts immediately above 500,000 coins, flag for soft review
        if new_amount > 500_000 and source != 'script':
            return True, f"Initial unverified entry of {new_amount:,} coins flagged for initial baseline verification."
        return False, None

    latest_entry = history[0]
    delta = new_amount - latest_entry.amount
    
    t1 = logged_at if logged_at.tzinfo is not None else logged_at.replace(tzinfo=timezone.utc)
    t0 = latest_entry.created_at if latest_entry.created_at.tzinfo is not None else latest_entry.created_at.replace(tzinfo=timezone.utc)
    time_diff = abs((t1 - t0).total_seconds())

    # 3. Sudden massive jump in short timeframe
    # E.g. Jumping +75,000 coins in under 6 hours without script
    if delta > 75_000 and time_diff < 21600 and source != 'script':
        return True, f"Sudden surge of +{delta:,} coins within {int(time_diff / 3600)}h flagged for manual review."

    # 4. Statistical Z-Score outlier check on historical deltas
    deltas = []
    for i in range(len(history) - 1):
        d = history[i].amount - history[i+1].amount
        deltas.append(d)

    if len(deltas) >= 5:
        mean_d = sum(deltas) / len(deltas)
        variance = sum((x - mean_d) ** 2 for x in deltas) / len(deltas)
        std_dev = math.sqrt(variance)

        if std_dev > 0:
            z_score = (delta - mean_d) / std_dev
            if z_score > 4.0 and delta > 30_000:
                return True, f"Outlier detected: gain of +{delta:,} coins has statistical Z-score of {z_score:.2f} (above 4.0 threshold)."

    return False, None
