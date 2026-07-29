from app.models import User
from app.extensions import db

def test_registration_success(client, app):
    response = client.post('/auth/register', data={
        'full_name': 'New User',
        'email': 'new@test.com',
        'username': 'newuser',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful. Please log in.' in response.data
    
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.check_password('password123')

def test_registration_duplicate_username(client, regular_user):
    response = client.post('/auth/register', data={
        'full_name': 'Another User',
        'email': 'another@test.com',
        'username': 'regular_user',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Username already exists' in response.data

def test_login_success(client, regular_user):
    response = client.post('/auth/login', data={
        'identifier': 'regular_user',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login successful.' in response.data
    assert b'Logout' in response.data # Check session persistence via UI presence

def test_login_invalid_credentials(client, regular_user):
    with client:
        response = client.post('/auth/login', data={
            'identifier': 'regular_user',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # User should not be logged in (dashboard redirects to login)
        response = client.get('/dashboard/', follow_redirects=False)
        assert response.status_code == 302

def test_logout(client, regular_user):
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'})
    response = client.get('/auth/logout', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_unauthorized_access_redirection(client):
    # Try to access dashboard without logging in
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in first.' in response.data
    assert b'Login' in response.data

def test_auth_edge_cases(client, regular_user, app, db):
    # 1. Authenticated user accessing register
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'})
    response = client.get('/auth/register', follow_redirects=False)
    assert response.status_code == 302
    
    # 2. Authenticated user accessing login
    response = client.get('/auth/login', follow_redirects=False)
    assert response.status_code == 302
    
    client.get('/auth/logout')
    
    # 3. Missing fields in register
    response = client.post('/auth/register', data={}, follow_redirects=True)
    assert b'All fields are required' in response.data
    
    # 4. Passwords do not match
    response = client.post('/auth/register', data={
        'full_name': 'A', 'username': 'a', 'email': 'a@a.com', 'password': 'pwd', 'confirm_password': 'dif'
    }, follow_redirects=True)
    assert b'Passwords do not match' in response.data
    
    # 5. Password too short
    response = client.post('/auth/register', data={
        'full_name': 'A', 'username': 'a', 'email': 'a@a.com', 'password': 'short', 'confirm_password': 'short'
    }, follow_redirects=True)
    assert b'Password must be at least 8 characters' in response.data
    
    # 6. Invalid email format
    response = client.post('/auth/register', data={
        'full_name': 'A', 'username': 'a', 'email': 'notanemail', 'password': 'password123', 'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'Invalid email format' in response.data
    
    # 7. Reserved username
    response = client.post('/auth/register', data={
        'full_name': 'A', 'username': 'admin', 'email': 'a@a.com', 'password': 'password123', 'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'Username is reserved' in response.data
    
    # 8. Duplicate email
    response = client.post('/auth/register', data={
        'full_name': 'B', 'username': 'buser', 'email': 'user@test.com', 'password': 'password123', 'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'Email already exists' in response.data
    
    # 9. Missing fields in login
    response = client.post('/auth/login', data={}, follow_redirects=True)
    assert b'Both fields are required' in response.data
    
    # 10. Login with inactive account
    with app.app_context():
        regular_user.is_active = False
        db.session.commit()
        
    response = client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'}, follow_redirects=True)
    assert b'Account is inactive' in response.data
