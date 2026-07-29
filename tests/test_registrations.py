from app.models import Registration

def test_register_success(client, regular_user, test_event):
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'}, follow_redirects=True)
    
    response = client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    
    reg = Registration.query.filter_by(user_id=regular_user.user_id, event_id=test_event.event_id).first()
    assert reg is not None
    assert reg.status == 'registered'

def test_duplicate_registration_prevention(client, regular_user, test_event):
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'}, follow_redirects=True)
    
    # First registration
    client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
    
    # Duplicate registration
    response = client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
    assert b'You are already registered for this event.' in response.data

def test_capacity_enforcement(client, app, test_event, db):
    # Set capacity to 1
    test_event.capacity = 1
    db.session.commit()
    
    # User 1 registers
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'}, follow_redirects=True)
    client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
    client.get('/auth/logout')
    
    # User 2 tries to register
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'}, follow_redirects=True)
    response = client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
    
    with app.app_context():
        count = Registration.query.filter_by(event_id=test_event.event_id).count()
        assert count == 1 # Only the first registration succeeded

def test_cancel_registration(client, regular_user, test_event):
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'}, follow_redirects=True)
    
    # Register
    client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
    
    # Get registration ID
    reg = Registration.query.filter_by(user_id=regular_user.user_id, event_id=test_event.event_id).first()
    
    # Cancel
    response = client.post(f'/registrations/cancel/{reg.registration_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration cancelled successfully.' in response.data
    
    reg_updated = Registration.query.get(reg.registration_id)
    assert reg_updated.status == 'cancelled'
