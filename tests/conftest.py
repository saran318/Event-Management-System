import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User, Event
from config import Config
from datetime import datetime, timedelta, time

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False
    
    # Mailman locmem backend for testing
    MAIL_BACKEND = 'locmem'

@pytest.fixture(scope='function')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def db(app):
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()

@pytest.fixture(scope='function')
def client(app, db):
    return app.test_client()

@pytest.fixture(scope='function')
def regular_user(db):
    user = User(
        full_name="Regular User",
        email="user@test.com",
        username="regular_user",
        role="user"
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture(scope='function')
def admin_user(db):
    user = User(
        full_name="Admin User",
        email="admin@test.com",
        username="admin_user",
        role="admin"
    )
    user.set_password("adminpass123")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture(scope='function')
def test_event(db, admin_user):
    event = Event(
        event_name="Test Event",
        event_type="Conference",
        description="A great test event",
        event_date=datetime.now().date() + timedelta(days=5),
        event_time=time(10, 0),
        venue="Main Hall",
        organizer="Admin Team",
        capacity=5
    )
    db.session.add(event)
    db.session.commit()
    return event
