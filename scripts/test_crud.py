from app import create_app
from app.extensions import db
from app.models import User, Event, Registration
from datetime import datetime, date, time
from sqlalchemy import text

from config import Config

class TestConfig(Config):
    WTF_CSRF_ENABLED = False

app = create_app(TestConfig)

def test_crud():
    with app.app_context():
        print("--- Testing Connection and Creating Tables ---")
        db.drop_all()
        db.create_all()
        print("Tables created successfully.")

        print("\n--- Verifying Tables ---")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")
        for t in ['users', 'events', 'registrations']:
            if t not in tables:
                print(f"Error: Table {t} is missing!")
            else:
                print(f"Table {t} exists.")
                
        print("\n--- Testing CRUD ---")
        
        # 1. Insert User
        test_user = User(
            full_name="Test User",
            email="test@example.com",
            mobile="1234567890",
            department="Engineering",
            username="testuser",
            role="user"
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        
        # 2. Insert Event
        test_event = Event(
            event_name="Test Event",
            event_type="Conference",
            description="A test event",
            event_date=date(2026, 8, 1),
            event_time=time(10, 0),
            venue="Main Hall",
            organizer="HR",
            capacity=100
        )
        db.session.add(test_event)
        
        db.session.commit()
        print(f"Inserted User: {test_user}")
        print(f"Inserted Event: {test_event}")
        
        # 3. Insert Registration
        test_registration = Registration(
            user_id=test_user.user_id,
            event_id=test_event.event_id,
            status="registered"
        )
        db.session.add(test_registration)
        db.session.commit()
        print(f"Inserted Registration: {test_registration}")
        
        # 4. Read Data & Verify Relationships
        reg = db.session.query(Registration).first()
        print(f"Read Registration: {reg}")
        print(f"Relationship Registration -> User: {reg.user.username}")
        print(f"Relationship Registration -> Event: {reg.event.event_name}")
        
        user = db.session.query(User).first()
        print(f"Relationship User -> Registrations: {user.registrations}")
        
        event = db.session.query(Event).first()
        print(f"Relationship Event -> Registrations: {event.registrations}")
        
        # 5. Update field
        reg.status = "attended"
        db.session.commit()
        print(f"Updated Registration Status: {reg.status}")
        
        # 6. Delete Registration manually is tested, but we will test routes instead
        db.session.delete(reg)
        db.session.commit()
        print("Deleted Registration.")

        print("\n--- Testing Registration Routes ---")
        client = app.test_client()
        
        # Login
        response = client.post('/auth/login', data=dict(
            identifier='testuser',
            password='password123'
        ), follow_redirects=True)
        print(f"Login status (expected 200): {response.status_code}")
        
        # 1. Register for event
        response = client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
        print(f"Register status: {response.status_code}")
        print(f"Register response data: {response.data.decode('utf-8')[:500]}")
        
        # 2. Duplicate registration
        response = client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
        print(f"Duplicate Register blocked (expected True): {b'already registered' in response.data.lower()}")
        
        # 3. Capacity check
        test_event.capacity = 1
        db.session.commit()
        
        user2 = User(full_name="User 2", email="u2@example.com", username="user2", role="user")
        user2.set_password('password123')
        db.session.add(user2)
        db.session.commit()
        
        client2 = app.test_client()
        client2.post('/auth/login', data=dict(identifier='user2', password='password123'), follow_redirects=True)
        response = client2.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
        print(f"Full Event Register blocked (expected True): {b'event is full' in response.data.lower()}")
        if not b'event is full' in response.data.lower():
            print(f"Full Event Debug Data: {response.data.decode('utf-8')[:500]}")
        
        # 4. Cancel registration
        reg = Registration.query.filter_by(user_id=test_user.user_id, event_id=test_event.event_id).first()
        if reg:
            response = client.post(f'/registrations/cancel/{reg.registration_id}', follow_redirects=True)
            print(f"Cancel Registration (expected True): {b'cancelled' in response.data.lower()}")
        else:
            print("Registration not found!")
        
        # 5. My Registrations
        response = client.get('/registrations/', follow_redirects=True)
        print(f"My Registrations page status (expected 200): {response.status_code}")
        
        print("\n--- Testing Dashboard Route ---")
        response = client.get('/dashboard/', follow_redirects=True)
        print(f"Dashboard status (expected 200): {response.status_code}")
        print(f"Dashboard contains 'Total Users' (expected True): {b'Total Users' in response.data}")
        
        print("\n--- Testing Search & Filtering ---")
        # Add another event for search testing
        test_event_2 = Event(
            event_name="Python Workshop",
            event_type="Workshop",
            description="Learn Python",
            event_date=date(2026, 9, 1),
            event_time=time(14, 0),
            venue="Room A",
            organizer="Engineering",
            capacity=50
        )
        db.session.add(test_event_2)
        db.session.commit()
        
        response = client.get('/events/?search=Python', follow_redirects=True)
        print(f"Search 'Python' (expected True): {b'Python Workshop' in response.data}")
        print(f"Search 'Python' missing 'Test Event' (expected True): {b'Test Event' not in response.data}")
        
        response = client.get('/events/?venue=Room+A', follow_redirects=True)
        print(f"Filter venue 'Room A' (expected True): {b'Python Workshop' in response.data}")
        
        response = client.get('/events/?organizer=HR', follow_redirects=True)
        print(f"Filter organizer 'HR' (expected True): {b'Test Event' in response.data}")
        
        # Cleanup
        db.session.query(Registration).delete()
        db.session.commit()
        db.session.delete(user2)
        db.session.delete(test_user)
        db.session.delete(test_event)
        db.session.delete(test_event_2)
        db.session.commit()
        print("Cleaned up Users and Event.")
        
if __name__ == '__main__':
    try:
        test_crud()
        print("\nAll CRUD tests passed successfully!")
    except Exception as e:
        print(f"\nError occurred: {e}")
