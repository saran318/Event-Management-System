import logging
from datetime import date, time, timedelta, datetime
from app import create_app
from app.extensions import db
from app.models import User, Event, Registration
from app.services import registration_service, event_service, email_service
from config import Config

logging.basicConfig(level=logging.ERROR)

class TestConfig(Config):
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 
    # Invalid SMTP config to force failure
    MAIL_SERVER = 'invalid.invalid'
    MAIL_PORT = 9999

app = create_app(TestConfig)

def test_email_flows():
    with app.app_context():
        db.create_all()

        user = User(full_name="Email Test User", email="test@test.com", username="testuser", role="user")
        user.set_password("pass")
        db.session.add(user)

        event = Event(event_name="Test Event", event_type="Conference", description="Desc",
                      event_date=datetime.now().date() + timedelta(days=5), event_time=time(10,0), venue="Hall A", organizer="HR", capacity=10)
        db.session.add(event)
        db.session.commit()
        
        # Test 1: Registration (SMTP will fail, but registration MUST succeed)
        print("Testing Registration (Expect SMTP Error in logs, but registration success)...")
        reg = registration_service.register_user_for_event(event.event_id, user)
        assert reg.status == 'registered'
        print("Registration Succeeded!")

        # Test 2: Event Update (SMTP will fail, update MUST succeed)
        print("\nTesting Event Update (Date change)...")
        update_data = {
            'title': 'Test Event',
            'event_type': 'Conference',
            'description': 'Desc',
            'venue': 'Hall A', # Same venue
            'organizer': 'HR',
            'capacity': 10,
            'event_date': (datetime.now().date() + timedelta(days=6)).strftime('%Y-%m-%d'),
            'event_time': '10:00'
        }
        updated_event = event_service.update_event(event.event_id, update_data)
        assert updated_event.event_date == datetime.now().date() + timedelta(days=6)
        print("Update Succeeded!")
        
        # Test 3: Venue Change
        print("\nTesting Venue Change...")
        venue_data = update_data.copy()
        venue_data['venue'] = 'Hall B'
        updated_event = event_service.update_event(event.event_id, venue_data)
        assert updated_event.venue == 'Hall B'
        print("Venue Update Succeeded!")

        # Test 4: Reminder Logic
        print("\nTesting Reminders...")
        # Artificially set event to 23.5 hours from now
        future = datetime.now() + timedelta(hours=23, minutes=30)
        updated_event.event_date = future.date()
        updated_event.event_time = future.time()
        db.session.commit()
        
        email_service.send_event_reminders()
        print("Reminders triggered successfully!")

        print("\nALL EMAIL FLOWS PASSED WITH SMTP DECOUPLING PROVEN.")

if __name__ == '__main__':
    test_email_flows()
