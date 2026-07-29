def test_admin_access_allowed(client, admin_user, test_event):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'}, follow_redirects=True)
    
    # Can access create event
    response = client.get('/events/create')
    assert response.status_code == 200
    
    # Can view participants
    response = client.get(f'/events/{test_event.event_id}/participants')
    assert response.status_code == 200

def test_regular_user_access_blocked(client, regular_user, test_event):
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'}, follow_redirects=True)
    
    # Cannot access create event
    response = client.get('/events/create', follow_redirects=False)
    assert response.status_code == 403
    
    # Cannot access participants
    response = client.get(f'/events/{test_event.event_id}/participants', follow_redirects=False)
    assert response.status_code == 403
    
    # Cannot delete event
    response = client.post(f'/events/delete/{test_event.event_id}', follow_redirects=True)
    assert response.status_code == 403
