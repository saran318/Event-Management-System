from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # Hashed password
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Relationship to Registration
    registrations = db.relationship('Registration', back_populates='user', lazy=True)

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(150), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_cancelled = db.Column(db.Boolean, default=False)

    # Relationship to Registration
    registrations = db.relationship('Registration', back_populates='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.event_name}>'

class Registration(db.Model):
    __tablename__ = 'registrations'

    registration_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='registered')

    # Unique constraint on (user_id, event_id)
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='uq_user_event_registration'),)

    # Relationships back to User and Event
    user = db.relationship('User', back_populates='registrations')
    event = db.relationship('Event', back_populates='registrations')

    def __repr__(self):
        return f'<Registration User:{self.user_id} Event:{self.event_id}>'
