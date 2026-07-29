from unittest.mock import patch
from app.services.registration_service import register_user_for_event
from app.services.event_service import update_event

@patch('app.services.email_service._send_email')
def test_registration_email_sent(mock_send_email, app, regular_user, test_event):
    with app.app_context():
        register_user_for_event(test_event.event_id, regular_user)
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        assert kwargs['recipient'] == regular_user.email
        assert "Registration Confirmed" in kwargs['subject']

@patch('app.services.email_service._send_email')
def test_event_update_email_sent(mock_send_email, app, regular_user, test_event):
    with app.app_context():
        # Register user first
        register_user_for_event(test_event.event_id, regular_user)
        mock_send_email.reset_mock()
        
        # Change venue
        update_event(
            event_id=test_event.event_id,
            data={
                'title': test_event.event_name,
                'event_type': test_event.event_type,
                'capacity': test_event.capacity,
                'description': test_event.description,
                'event_date': test_event.event_date.strftime('%Y-%m-%d'),
                'event_time': test_event.event_time.strftime('%H:%M'),
                'venue': "New Global Venue", # Changed
                'organizer': test_event.organizer
            }
        )
        
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        assert kwargs['recipient'] == regular_user.email
        assert "Venue Change" in kwargs['subject']
