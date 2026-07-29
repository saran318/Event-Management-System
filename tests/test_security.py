def test_csrf_missing(client):
    # Enable CSRF globally for this test only by mutating config (or test the app with CSRF enabled)
    # Actually, in testing WTF_CSRF_ENABLED is False by default. Let's flip it for a specific test.
    client.application.config['WTF_CSRF_ENABLED'] = True
    
    response = client.post('/auth/login', data={
        'identifier': 'user',
        'password': 'password'
    })
    
    # Missing CSRF token should return 400 Bad Request
    assert response.status_code == 400
    assert b'Bad Request' in response.data
    
    # Reset
    client.application.config['WTF_CSRF_ENABLED'] = False

def test_404_error_page(client):
    response = client.get('/this-route-does-not-exist')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data
    assert b'Return Home' in response.data

def test_malformed_url(client):
    response = client.get('/events/edit/abc', follow_redirects=True)
    assert response.status_code == 404 # Werkzeug routing blocks non-int parameters usually
    
def test_403_error_page(client, regular_user, test_event):
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'})
    response = client.get(f'/events/{test_event.event_id}/participants', follow_redirects=True)
    assert response.status_code == 403
    assert b'Access Denied' in response.data
