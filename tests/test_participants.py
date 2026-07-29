def test_participants_view_admin(client, admin_user, regular_user, test_event):
    # Register the regular user
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'}, follow_redirects=True)
    client.post(f'/registrations/register/{test_event.event_id}', follow_redirects=True)
    client.get('/auth/logout')
    
    # Login as admin to view participants
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'}, follow_redirects=True)
    response = client.get(f'/events/{test_event.event_id}/participants')
    
    assert response.status_code == 200
    assert b'Participants' in response.data

def test_participants_empty_state(client, admin_user, test_event):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'}, follow_redirects=True)
    response = client.get(f'/events/{test_event.event_id}/participants')
    
    assert response.status_code == 200
    assert b'No participants have registered for this event yet' in response.data

def test_participants_invalid_event(client, admin_user):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'})
    response = client.get('/events/9999/participants', follow_redirects=True)
    
    assert response.status_code == 404
