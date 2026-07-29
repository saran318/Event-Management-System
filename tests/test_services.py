import pytest
from app.services.event_service import create_event, update_event, get_event_by_id, delete_event, list_events
from app.services.registration_service import register_user_for_event, cancel_registration, list_user_registrations
from app.exceptions import EventValidationError, EventNotFoundError, EventOperationError
from app.models import Registration, Event
from datetime import datetime, timedelta, time

def test_create_event_validation_errors(app, admin_user, db):
    with app.app_context():
        # Missing fields
        with pytest.raises(EventValidationError):
            create_event({})
            
        # Invalid date format
        with pytest.raises(EventValidationError):
            create_event({'title': 'T', 'event_type': 'T', 'venue': 'V', 'organizer': 'O', 'capacity': '10', 'event_date': 'invalid', 'event_time': '10:00'})
            
        # Invalid time format
        with pytest.raises(EventValidationError):
            create_event({'title': 'T', 'event_type': 'T', 'venue': 'V', 'organizer': 'O', 'capacity': '10', 'event_date': '2030-01-01', 'event_time': 'invalid'})
            
        # Non-integer capacity
        with pytest.raises(EventValidationError):
            create_event({'title': 'T', 'event_type': 'T', 'venue': 'V', 'organizer': 'O', 'capacity': 'abc', 'event_date': '2030-01-01', 'event_time': '10:00'})

def test_update_event_validation_errors(app, admin_user, test_event, db):
    with app.app_context():
        # Invalid capacity update
        with pytest.raises(EventValidationError):
            update_event(test_event.event_id, {'title': 'T', 'event_type': 'T', 'venue': 'V', 'organizer': 'O', 'capacity': '0', 'event_date': '2030-01-01', 'event_time': '10:00'})
            
        # Update non-existent event
        with pytest.raises(EventNotFoundError):
            update_event(9999, {})

def test_delete_nonexistent_event(app, db):
    with app.app_context():
        with pytest.raises(EventNotFoundError):
            delete_event(9999)

def test_get_nonexistent_event(app, db):
    with app.app_context():
        with pytest.raises(EventNotFoundError):
            get_event_by_id(9999)

def test_registration_validation_errors(app, regular_user, test_event, db):
    with app.app_context():
        # Register for non-existent event
        with pytest.raises(EventNotFoundError):
            register_user_for_event(9999, regular_user)
            
        # Duplicate registration
        register_user_for_event(test_event.event_id, regular_user)
        with pytest.raises(EventOperationError, match="already registered"):
            register_user_for_event(test_event.event_id, regular_user)
            
        # Cancel non-existent registration
        with pytest.raises(EventNotFoundError):
            cancel_registration(9999, regular_user)
            
def test_cancel_registration_unauthorized(app, regular_user, admin_user, test_event, db):
    with app.app_context():
        register_user_for_event(test_event.event_id, regular_user)
        reg = Registration.query.filter_by(user_id=regular_user.user_id).first()
        
        # admin_user cannot cancel regular_user's registration
        with pytest.raises(EventOperationError, match="Unauthorized"):
            cancel_registration(reg.registration_id, admin_user)

def test_registration_service_edge_cases(app, regular_user, admin_user, db):
    with app.app_context():
        past_event = Event(
            event_name='Past', event_type='Conference', venue='V', organizer='O',
            capacity=10, event_date=(datetime.now() - timedelta(days=5)).date(),
            event_time=datetime.strptime('10:00', '%H:%M').time()
        )
        db.session.add(past_event)
        db.session.commit()
        
        # 1. Past event registration
        with pytest.raises(EventOperationError, match="past event"):
            register_user_for_event(past_event.event_id, regular_user)
            
        # Create a future event
        future_event = create_event({
            'title': 'Future', 'event_type': 'Conference', 'venue': 'V', 'organizer': 'O',
            'capacity': 1, 'event_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'event_time': '10:00'
        })
        
        # 2. Re-registering after cancellation & Cancelling already cancelled
        reg = register_user_for_event(future_event.event_id, regular_user)
        cancel_registration(reg.registration_id, regular_user)
        
        # Cancel again
        with pytest.raises(EventOperationError, match="already cancelled"):
            cancel_registration(reg.registration_id, regular_user)
            
        # Re-register
        reg2 = register_user_for_event(future_event.event_id, regular_user)
        assert reg2.status == 'registered'
        assert reg2.registration_id == reg.registration_id
        
        # 3. Event full when re-registering
        # user1 is registered, so capacity (1) is full.
        # If user1 cancels, and user2 registers, capacity is full. Then user1 tries to re-register.
        cancel_registration(reg2.registration_id, regular_user)
        
        from app.models import User
        user2 = User(username='user2', email='u2@u.com', full_name='U2', role='user', is_active=True)
        user2.set_password('pwd')
        db.session.add(user2)
        db.session.commit()
        
        register_user_for_event(future_event.event_id, user2)
        
        # Now regular_user tries to re-register, but capacity is full
        with pytest.raises(EventOperationError, match="event is full"):
            register_user_for_event(future_event.event_id, regular_user)

def test_event_service_create(app, admin_user):
    with app.app_context():
        event = create_event({
            'title': 'Service Event',
            'event_type': 'Meetup',
            'capacity': 10,
            'description': 'Test',
            'event_date': (datetime.now().date() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'event_time': '10:00',
            'venue': 'Service Room',
            'organizer': 'Service Org'
        })
        assert event.event_id is not None
        assert event.event_name == 'Service Event'

def test_registration_service_logic(app, admin_user, regular_user, test_event):
    with app.app_context():
        # Register
        reg = register_user_for_event(test_event.event_id, regular_user)
        assert reg.status == 'registered'
        
        # Test duplicate
        with pytest.raises(Exception, match="already registered"):
            register_user_for_event(test_event.event_id, regular_user)
            
        # Cancel
        cancel_registration(reg.registration_id, regular_user)
        assert reg.status == 'cancelled'

def test_registration_capacity_logic(app, regular_user, admin_user, test_event):
    with app.app_context():
        test_event.capacity = 1
        app.extensions['sqlalchemy'].session.commit()
        
        register_user_for_event(test_event.event_id, regular_user)
        
        # Next registration should fail
        with pytest.raises(Exception, match="full"):
            register_user_for_event(test_event.event_id, admin_user)
