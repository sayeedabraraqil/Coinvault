import os
from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, login_manager, csrf, limiter, socketio
from app.models.user import User

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # Register Template Filters
    @app.template_filter('format_number')
    def format_number(value):
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return value

    # Security Headers Hook
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # CSP: allows self scripts, fonts, inline styles with hash/safe, WebGL canvas
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://api.dicebear.com; "
            "style-src 'self' 'unsafe-inline'; "
            "font-src 'self' data:; "
            "img-src 'self' data: https://api.dicebear.com https://flagcdn.com; "
            "connect-src 'self' ws: wss: http: https:;"
        )
        return response

    # Global Template Context
    @app.context_processor
    def inject_globals():
        return {
            'PLATFORM_NAME': 'COINVAULT',
            'PLATFORM_TAGLINE': 'The eFootball Wealth & Rank Terminal',
            'CURRENT_YEAR': 2026
        }

    return app
