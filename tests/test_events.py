from datetime import datetime, timedelta
from app.models import Event
from app.extensions import db

def test_create_event_success(client, admin_user):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'}, follow_redirects=True)
    
    date_str = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    response = client.post('/events/create', data={
        'title': 'New Test Event',
        'event_type': 'Workshop',
        'capacity': '50',
        'description': 'A new event',
        'event_date': date_str,
        'event_time': '14:00',
        'venue': 'Room 101',
        'organizer': 'Admin Team'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Event Created Successfully' in response.data
    event = Event.query.filter_by(event_name='New Test Event').first()
    assert event is not None

def test_create_event_invalid_capacity(client, admin_user):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'}, follow_redirects=True)
    
    date_str = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    response = client.post('/events/create', data={
        'title': 'Bad Capacity Event',
        'event_type': 'Workshop',
        'capacity': '0', # Invalid capacity
        'description': 'A new event',
        'event_date': date_str,
        'event_time': '14:00',
        'venue': 'Room 101',
        'organizer': 'Admin Team'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Capacity must be greater than 0.' in response.data

def test_edit_event(client, admin_user, test_event):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'}, follow_redirects=True)
    
    response = client.post(f'/events/edit/{test_event.event_id}', data={
        'title': 'Updated Event Title',
        'event_type': test_event.event_type,
        'capacity': test_event.capacity,
        'description': test_event.description,
        'event_date': test_event.event_date.strftime('%Y-%m-%d'),
        'event_time': test_event.event_time.strftime('%H:%M'),
        'venue': 'New Venue',
        'organizer': test_event.organizer
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Event Updated Successfully' in response.data
    
    event = Event.query.get(test_event.event_id)
    assert event.event_name == 'Updated Event Title'
    assert event.venue == 'New Venue'

def test_delete_event(client, admin_user, test_event):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'})
    
    response = client.post(f'/events/delete/{test_event.event_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Event Deleted Successfully' in response.data
    
    event = Event.query.get(test_event.event_id)
    assert event is None

def test_missing_event(client):
    response = client.get('/events/99999', follow_redirects=True)
    assert response.status_code == 404
    assert b'Page Not Found' in response.data
