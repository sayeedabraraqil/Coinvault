import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app.extensions import db, limiter, socketio
from app.models.user import User, ApiToken
from app.models.coin import CoinEntry
from app.models.social import Follow, Badge, UserBadge
from app.forms.coin import LogCoinForm, EditCoinForm
from app.forms.profile import ProfileForm, ApiTokenForm
from app.services.anti_cheat import evaluate_entry_for_outliers
from app.services.analytics import compute_user_analytics
from app.services.badges import check_and_award_user_badges
from app.services.audit import log_audit

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    stats = compute_user_analytics(current_user.id)
    log_form = LogCoinForm()
    
    # Recent active entries (up to 25)
    entries = CoinEntry.query.filter_by(user_id=current_user.id, is_deleted=False)\
        .order_by(CoinEntry.logged_at.desc()).limit(25).all()

    # User's unlocked badges
    unlocked_badges = current_user.user_badges.all()
    
    # Rivals (users 2 ranks above and 2 ranks below current user)
    rivals = []
    if stats.get('rank'):
        all_public = User.query.filter_by(is_banned=False, is_private=False).all()
        ranked_list = sorted([(u, u.current_balance) for u in all_public], key=lambda x: x[1], reverse=True)
        my_idx = next((i for i, item in enumerate(ranked_list) if item[0].id == current_user.id), None)
        if my_idx is not None:
            start_i = max(0, my_idx - 2)
            end_i = min(len(ranked_list), my_idx + 3)
            for idx in range(start_i, end_i):
                u, bal = ranked_list[idx]
                rivals.append({
                    'rank': idx + 1,
                    'user': u,
                    'balance': bal,
                    'gap': bal - stats['current_balance'],
                    'is_self': u.id == current_user.id
                })

    return render_template(
        'dashboard/index.html',
        stats=stats,
        entries=entries,
        log_form=log_form,
        unlocked_badges=unlocked_badges,
        rivals=rivals
    )

@user_bp.route('/coins/log', methods=['POST'])
@login_required
@limiter.limit("60 per hour")
def log_coin():
    form = LogCoinForm()
    if form.validate_on_submit():
        amount = form.amount.data
        note = form.note.data.strip() if form.note.data else None
        
        # Handle optional backdating
        logged_at = datetime.now(timezone.utc)
        if form.logged_at.data:
            logged_at = form.logged_at.data.replace(tzinfo=timezone.utc)

        # Duplicate submit check (same amount logged within last 10 seconds)
        last_entry = CoinEntry.query.filter_by(user_id=current_user.id, is_deleted=False)\
            .order_by(CoinEntry.created_at.desc()).first()
        if last_entry and last_entry.amount == amount:
            time_since = (datetime.now(timezone.utc) - last_entry.created_at.replace(tzinfo=timezone.utc)).total_seconds()
            if time_since < 10:
                flash('Duplicate snapshot detected: you submitted this identical amount seconds ago.', 'warning')
                return redirect(url_for('user.dashboard'))

        # Outlier Detection
        is_flagged, flag_reason = evaluate_entry_for_outliers(current_user, amount, logged_at, 'self')

        entry = CoinEntry(
            user_id=current_user.id,
            amount=amount,
            source='self',
            note=note,
            logged_at=logged_at,
            is_flagged=is_flagged,
            flag_reason=flag_reason
        )
        db.session.add(entry)
        db.session.commit()

        # Audit log
        log_audit(current_user.id, 'ENTRY_CREATE', 'CoinEntry', entry.id, None, entry.to_dict(), request)

        # Award Badges
        check_and_award_user_badges(current_user)

        # Broadcast real-time feed via SocketIO
        try:
            delta = amount - (last_entry.amount if last_entry else 0)
            socketio.emit('activity_feed', {
                'username': current_user.username,
                'display_name': current_user.effective_name,
                'avatar_url': current_user.avatar_url,
                'amount': amount,
                'delta': delta,
                'source': 'self',
                'timestamp': datetime.now(timezone.utc).strftime('%H:%M:%S')
            })
        except Exception:
            pass

        if is_flagged:
            flash(f'Balance logged ({amount:,} coins). Note: Our anomaly filter flagged this snapshot for moderation ({flag_reason}).', 'warning')
        else:
            flash(f'Successfully logged vault balance: {amount:,} eFootball coins.', 'success')

    return redirect(url_for('user.dashboard'))

@user_bp.route('/coins/<int:entry_id>/edit', methods=['POST'])
@login_required
def edit_coin(entry_id):
    entry = CoinEntry.query.filter_by(id=entry_id, user_id=current_user.id, is_deleted=False).first_or_404()
    form = EditCoinForm()
    if form.validate_on_submit():
        old_val = entry.to_dict()
        entry.amount = form.amount.data
        if form.note.data:
            entry.note = form.note.data.strip()
        entry.updated_at = datetime.now(timezone.utc)
        
        # Re-check outlier
        is_flagged, flag_reason = evaluate_entry_for_outliers(current_user, entry.amount, entry.logged_at, entry.source)
        entry.is_flagged = is_flagged
        entry.flag_reason = flag_reason
        
        db.session.commit()
        log_audit(current_user.id, 'ENTRY_EDIT', 'CoinEntry', entry.id, old_val, entry.to_dict(), request)
        flash('Snapshot updated with audit log preserved.', 'info')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/coins/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_coin(entry_id):
    entry = CoinEntry.query.filter_by(id=entry_id, user_id=current_user.id, is_deleted=False).first_or_404()
    old_val = entry.to_dict()
    entry.is_deleted = True
    entry.deleted_at = datetime.now(timezone.utc)
    db.session.commit()

    log_audit(current_user.id, 'ENTRY_DELETE', 'CoinEntry', entry.id, old_val, {'is_deleted': True}, request)
    flash('Coin snapshot archived (immutable audit history preserved).', 'info')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username.lower()).first_or_404()
    if user.is_private and (not current_user.is_authenticated or current_user.id != user.id):
        return render_template('user/private_profile.html', user=user)

    stats = compute_user_analytics(user.id)
    badges = user.user_badges.all()
    is_following = current_user.is_authenticated and current_user.is_following(user)

    return render_template(
        'user/profile.html',
        profile_user=user,
        stats=stats,
        badges=badges,
        is_following=is_following
    )

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile_form = ProfileForm(obj=current_user)
    token_form = ApiTokenForm()
    
    if profile_form.validate_on_submit() and 'submit' in request.form and request.form['submit'] == profile_form.submit.label.text:
        old_val = current_user.to_dict(include_private=True)
        
        current_user.display_name = profile_form.display_name.data.strip() or None
        current_user.efootball_id = profile_form.efootball_id.data.strip() or None
        current_user.bio = profile_form.bio.data.strip() or None
        current_user.country = profile_form.country.data
        current_user.is_private = profile_form.is_private.data
        
        # Handle Avatar Upload with Pillow validation & resizing
        avatar_file = profile_form.avatar.data
        if avatar_file and hasattr(avatar_file, 'filename') and avatar_file.filename:
            try:
                # Open with Pillow to verify valid image
                img = Image.open(avatar_file)
                img.verify() # verify integrity
                
                # Reopen to convert & resize
                avatar_file.seek(0)
                img = Image.open(avatar_file)
                img = img.convert('RGB')
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                ext = 'webp'
                filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                dest_path = upload_dir / filename
                img.save(dest_path, 'WEBP', quality=88)
                
                # Delete old avatar if present
                if current_user.avatar_filename:
                    old_path = upload_dir / current_user.avatar_filename
                    if old_path.exists() and old_path.is_file():
                        try:
                            old_path.unlink()
                        except Exception:
                            pass
                            
                current_user.avatar_filename = filename
            except Exception as e:
                flash(f'Failed to process avatar image: {str(e)}', 'danger')

        db.session.commit()
        log_audit(current_user.id, 'PROFILE_UPDATE', 'User', current_user.id, old_val, current_user.to_dict(include_private=True), request)
        flash('Terminal settings updated successfully.', 'success')
        return redirect(url_for('user.settings'))

    tokens = ApiToken.query.filter_by(user_id=current_user.id, revoked=False).order_by(ApiToken.created_at.desc()).all()
    return render_template('user/settings.html', profile_form=profile_form, token_form=token_form, tokens=tokens)

@user_bp.route('/settings/tokens/create', methods=['POST'])
@login_required
def create_token():
    form = ApiTokenForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        raw_token, prefix, token_hash = ApiToken.generate_token()
        
        token = ApiToken(
            user_id=current_user.id,
            name=name,
            prefix=prefix,
            token_hash=token_hash
        )
        db.session.add(token)
        db.session.commit()

        log_audit(current_user.id, 'TOKEN_CREATE', 'ApiToken', token.id, None, {'name': name, 'prefix': prefix}, request)
        
        # Display the full raw token in session flash
        flash(f"__NEW_API_TOKEN__:{raw_token}", 'token_generated')
        return redirect(url_for('user.settings'))
    
    flash('Invalid token label.', 'danger')
    return redirect(url_for('user.settings'))

@user_bp.route('/settings/tokens/<int:token_id>/revoke', methods=['POST'])
@login_required
def revoke_token(token_id):
    token = ApiToken.query.filter_by(id=token_id, user_id=current_user.id).first_or_404()
    token.revoked = True
    db.session.commit()
    log_audit(current_user.id, 'TOKEN_REVOKE', 'ApiToken', token.id, None, {'revoked': True}, request)
    flash(f"API token '{token.name}' ({token.prefix}...) revoked.", 'info')
    return redirect(url_for('user.settings'))

@user_bp.route('/follow/<int:target_user_id>', methods=['POST'])
@login_required
def toggle_follow(target_user_id):
    if target_user_id == current_user.id:
        flash('You cannot rival or follow yourself.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    target_user = User.query.get_or_404(target_user_id)
    if current_user.is_following(target_user):
        current_user.unfollow(target_user)
        db.session.commit()
        flash(f"Unfollowed {target_user.effective_name}.", 'info')
    else:
        current_user.follow(target_user)
        db.session.commit()
        flash(f"Now tracking {target_user.effective_name} in your watchlist.", 'success')

    next_page = request.referrer or url_for('user.profile', username=target_user.username)
    return redirect(next_page)
