from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models.user import User
from app.forms.auth import LoginForm, RegisterForm, RequestResetForm, ResetPasswordForm
from app.services.audit import log_audit

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("20 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip().lower(),
            email=form.email.data.strip().lower(),
            display_name=form.username.data.strip()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        log_audit(user.id, 'USER_REGISTER', 'User', user.id, None, {'username': user.username}, request)
        flash('Terminal account initialized successfully! Sign in to enter the vault.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("30 per hour")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        identity = form.identity.data.strip().lower()
        user = User.query.filter(
            (User.username == identity) | (User.email == identity)
        ).first()

        if user and user.check_password(form.password.data):
            if user.is_banned:
                flash('Access denied: This terminal account has been suspended for policy violations.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            log_audit(user.id, 'USER_LOGIN', 'User', user.id, None, None, request)
            flash(f'Welcome back to the terminal, {user.effective_name}.', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid credentials. Check your username/email and password.', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    log_audit(current_user.id, 'USER_LOGOUT', 'User', current_user.id, None, None, request)
    logout_user()
    flash('Logged out of COINVAULT terminal.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            # Generate simulated reset token for dev / notification
            user.reset_token = "demo_reset_token"
            db.session.commit()
            flash('Password reset instructions have been dispatched to your email address.', 'info')
        else:
            flash('If an account exists with that email, instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
