from bs4 import BeautifulSoup

def test_frontend_dashboard(client, admin_user):
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'})
    response = client.get('/dashboard/')
    
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Verify responsive cards
    cards = soup.find_all(class_='card')
    assert len(cards) > 0
    
    # Verify specific layout components
    assert soup.find(class_='bi-people-fill') is not None
    assert soup.find(class_='bi-calendar-event-fill') is not None

def test_frontend_events_empty_state(client):
    # Without any events created
    response = client.get('/events/')
    soup = BeautifulSoup(response.data, 'html.parser')
    
    empty_state = soup.find(class_='empty-state')
    assert empty_state is not None
    assert 'No events available yet' in empty_state.text

def test_frontend_table_responsiveness(client, admin_user, test_event, regular_user):
    client.post('/auth/login', data={'identifier': 'regular_user', 'password': 'password123'})
    client.post(f'/registrations/register/{test_event.event_id}')
    client.get('/auth/logout')
    
    client.post('/auth/login', data={'identifier': 'admin_user', 'password': 'adminpass123'})
    response = client.get(f'/events/{test_event.event_id}/participants')
    
    soup = BeautifulSoup(response.data, 'html.parser')
    table_wrapper = soup.find(class_='table-responsive')
    assert table_wrapper is not None
    
    table = table_wrapper.find('table')
    assert 'table-hover' in table['class']
