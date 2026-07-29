from flask import Flask, redirect, url_for, render_template
from config import Config
from app.extensions import db, login_manager, csrf, mail
from flask_login import current_user
from flask_wtf.csrf import CSRFError

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.events import events_bp
    from app.routes.registrations import registrations_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(registrations_bp, url_prefix='/registrations')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('400.html', reason=e.description), 400

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app
