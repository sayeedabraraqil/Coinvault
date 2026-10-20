import csv
import io
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.coin import CoinEntry
from app.models.social import Report
from app.models.audit import AuditLog
from app.services.audit import log_audit

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        abort(403)

@admin_bp.route('/')
def dashboard():
    flagged_entries = CoinEntry.query.filter_by(is_flagged=True, is_deleted=False)\
        .order_by(CoinEntry.created_at.desc()).all()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(30).all()
    recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(25).all()
    reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).all()

    total_users = User.query.count()
    total_entries = CoinEntry.query.count()
    flagged_count = len(flagged_entries)

    return render_template(
        'admin/index.html',
        flagged_entries=flagged_entries,
        recent_users=recent_users,
        recent_audits=recent_audits,
        reports=reports,
        total_users=total_users,
        total_entries=total_entries,
        flagged_count=flagged_count
    )

@admin_bp.route('/entries/<int:entry_id>/approve', methods=['POST'])
def approve_entry(entry_id):
    entry = CoinEntry.query.get_or_404(entry_id)
    entry.is_flagged = False
    entry.flag_reason = f"Approved by admin @{current_user.username}"
    db.session.commit()
    log_audit(current_user.id, 'ADMIN_APPROVE_ENTRY', 'CoinEntry', entry.id, None, entry.to_dict(), request)
    flash(f"Entry #{entry.id} cleared and verified for leaderboards.", 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/entries/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    entry = CoinEntry.query.get_or_404(entry_id)
    entry.is_deleted = True
    entry.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    log_audit(current_user.id, 'ADMIN_DELETE_ENTRY', 'CoinEntry', entry.id, None, {'is_deleted': True}, request)
    flash(f"Fraudulent entry #{entry.id} archived and purged from leaderboards.", 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<int:user_id>/toggle-ban', methods=['POST'])
def toggle_ban(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot ban your own administrative account.", 'danger')
        return redirect(url_for('admin.dashboard'))

    user.is_banned = not user.is_banned
    db.session.commit()
    action = 'ADMIN_BAN_USER' if user.is_banned else 'ADMIN_UNBAN_USER'
    log_audit(current_user.id, action, 'User', user.id, None, {'is_banned': user.is_banned}, request)
    flash(f"User @{user.username} {'suspended' if user.is_banned else 'restored'}.", 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export/csv')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Entry ID', 'User ID', 'Username', 'Amount', 'Source', 'Flagged', 'Flag Reason', 'Logged At', 'Created At'])

    entries = CoinEntry.query.join(User).filter(CoinEntry.is_deleted == False).order_by(CoinEntry.id.desc()).all()
    for e in entries:
        writer.writerow([
            e.id,
            e.user_id,
            e.user.username,
            e.amount,
            e.source,
            e.is_flagged,
            e.flag_reason or '',
            e.logged_at.isoformat(),
            e.created_at.isoformat()
        ])

    log_audit(current_user.id, 'ADMIN_EXPORT_CSV', 'CoinEntry', None, None, {'count': len(entries)}, request)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename=coinvault_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )
