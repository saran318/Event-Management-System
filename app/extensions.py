from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mailman import Mail

# Single shared instances
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in first."
login_manager.session_protection = "strong"
