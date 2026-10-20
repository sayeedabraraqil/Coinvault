import hashlib
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.extensions import db, limiter, socketio, csrf
from app.models.user import User, ApiToken
from app.models.coin import CoinEntry
from app.services.anti_cheat import evaluate_entry_for_outliers
from app.services.badges import check_and_award_user_badges, award_badge_if_earned
from app.services.audit import log_audit

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Exempt external API webhook endpoints from CSRF
csrf.exempt(api_bp)

def authenticate_bearer():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, ("Missing or malformed Authorization header (Bearer token required)", 401)
    
    raw_token = auth_header.split(' ', 1)[1].strip()
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    
    api_token = ApiToken.query.filter_by(token_hash=token_hash, revoked=False).first()
    if not api_token:
        return None, ("Invalid or revoked API token", 403)
        
    api_token.last_used_at = datetime.now(timezone.utc)
    db.session.commit()
    return api_token.user, None

@api_bp.route('/coins/log', methods=['POST'])
@limiter.limit("120 per hour")
def log_coin_via_script():
    """
    Dedicated endpoint for the Tampermonkey companion userscript.
    Receives verified balance readings directly from the user's active session.
    """
    user, err = authenticate_bearer()
    if err:
        return jsonify({'error': err[0]}), err[1]
    
    if user.is_banned:
        return jsonify({'error': 'Account suspended'}), 403

    data = request.get_json(silent=True) or {}
    amount_raw = data.get('amount')
    note = data.get('note', 'Auto-logged via COINVAULT Tampermonkey Script')
    
    try:
        amount = int(amount_raw)
        if amount < 0 or amount > 20_000_000:
            return jsonify({'error': 'Invalid amount: must be non-negative and <= 20,000,000'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Amount must be an integer'}), 400

    # Avoid logging redundant duplicate reading within 30 seconds
    last_entry = CoinEntry.query.filter_by(user_id=user.id, is_deleted=False)\
        .order_by(CoinEntry.created_at.desc()).first()
    if last_entry and last_entry.amount == amount:
        time_diff = (datetime.now(timezone.utc) - last_entry.created_at.replace(tzinfo=timezone.utc)).total_seconds()
        if time_diff < 30:
            return jsonify({
                'status': 'skipped',
                'message': 'Identical balance recently recorded. Snapshot skipped to prevent duplicates.',
                'amount': amount
            }), 200

    # Evaluate for outliers
    now = datetime.now(timezone.utc)
    is_flagged, flag_reason = evaluate_entry_for_outliers(user, amount, now, 'script')

    entry = CoinEntry(
        user_id=user.id,
        amount=amount,
        source='script',
        note=note,
        logged_at=now,
        is_flagged=is_flagged,
        flag_reason=flag_reason
    )
    db.session.add(entry)
    db.session.commit()

    log_audit(user.id, 'SCRIPT_ENTRY_CREATE', 'CoinEntry', entry.id, None, entry.to_dict(), request)

    # Award "Direct Terminal Link" badge
    award_badge_if_earned(user, 'verified_source')
    check_and_award_user_badges(user)

    # Broadcast socket live update
    try:
        delta = amount - (last_entry.amount if last_entry else 0)
        socketio.emit('activity_feed', {
            'username': user.username,
            'display_name': user.effective_name,
            'avatar_url': user.avatar_url,
            'amount': amount,
            'delta': delta,
            'source': 'script',
            'timestamp': now.strftime('%H:%M:%S')
        })
    except Exception:
        pass

    return jsonify({
        'status': 'success',
        'entry_id': entry.id,
        'amount': entry.amount,
        'source': 'script',
        'is_flagged': entry.is_flagged,
        'flag_reason': entry.flag_reason,
        'logged_at': entry.logged_at.isoformat()
    }), 201

@api_bp.route('/search/users', methods=['GET'])
@limiter.limit("120 per minute")
def search_users():
    """Endpoint for Command Palette (Cmd+K) instant search."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    users = User.query.filter(
        User.is_banned == False,
        User.is_private == False,
        (User.username.ilike(f"%{q}%")) | (User.display_name.ilike(f"%{q}%")) | (User.efootball_id.ilike(f"%{q}%"))
    ).limit(8).all()

    results = []
    for u in users:
        results.append({
            'username': u.username,
            'display_name': u.effective_name,
            'avatar_url': u.avatar_url,
            'balance': u.current_balance,
            'url': f"/profile/{u.username}"
        })

    return jsonify(results)

@api_bp.route('/user/<username>/chart', methods=['GET'])
def get_user_chart(username):
    user = User.query.filter_by(username=username.lower(), is_banned=False).first_or_404()
    entries = CoinEntry.query.filter_by(user_id=user.id, is_deleted=False)\
        .order_by(CoinEntry.logged_at.asc()).all()

    labels = [e.logged_at.strftime('%Y-%m-%d %H:%M') for e in entries]
    values = [e.amount for e in entries]

    return jsonify({
        'username': user.username,
        'labels': labels,
        'values': values
    })
