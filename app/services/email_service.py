import logging
from datetime import datetime, timedelta
from flask import render_template
from flask_mailman import EmailMultiAlternatives
from app.models import Registration, Event

logger = logging.getLogger(__name__)

import threading
from flask import current_app

def _send_async_email(app, subject, recipient, txt_body, html_body):
    """Background thread function to send the email."""
    with app.app_context():
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=txt_body,
                to=[recipient]
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
        except Exception as e:
            logger.exception(f"Failed to send email '{subject}' to {recipient}: {e}")

def _send_email(subject, recipient, template, **kwargs):
    """
    Private helper function to construct and send HTML/TXT emails asynchronously.
    Silently catches and logs SMTP exceptions to prevent upstream failures.
    """
    try:
        html_body = render_template(f"emails/{template}.html", **kwargs)
        txt_body = render_template(f"emails/{template}.txt", **kwargs)
        
        # Run the actual send operation in a background thread to prevent blocking
        app = current_app._get_current_object()
        thread = threading.Thread(target=_send_async_email, args=(app, subject, recipient, txt_body, html_body))
        thread.start()
    except Exception as e:
        logger.exception(f"Failed to prepare email '{subject}' for {recipient}: {e}")

def send_registration_confirmation(user, event):
    """Sends a confirmation email after successful registration."""
    _send_email(
        subject=f"Registration Confirmed: {event.event_name}",
        recipient=user.email,
        template="confirmation",
        user=user,
        event=event
    )

def send_event_update_notification(user, event, changed_fields):
    """Sends an email detailing generic modifications to an event."""
    _send_email(
        subject=f"Update: {event.event_name} Details Changed",
        recipient=user.email,
        template="event_update",
        user=user,
        event=event,
        changed_fields=changed_fields
    )

def send_venue_change_notification(user, event, old_venue, new_venue):
    """Sends a specific email alerting users of a venue relocation."""
    _send_email(
        subject=f"URGENT: Venue Change for {event.event_name}",
        recipient=user.email,
        template="venue_change",
        user=user,
        event=event,
        old_venue=old_venue,
        new_venue=new_venue
    )

def send_event_cancellation_notification(user, event):
    """Sends an email alerting users that an event has been cancelled."""
    _send_email(
        subject=f"CANCELLED: {event.event_name}",
        recipient=user.email,
        template="event_cancellation",
        user=user,
        event=event
    )

def send_event_reminders():
    """
    Finds events occurring in the next 24 hours and sends reminders to confirmed participants.
    Designed to be run safely by a background cron job or task scheduler.
    """
    now = datetime.now()
    
    # We filter by events occurring within the next 24 hour window
    # Assuming event_date and event_time represent the start
    
    events = Event.query.all()
    for event in events:
        event_datetime = datetime.combine(event.event_date, event.event_time)
        time_until_event = event_datetime - now
        
        # If the event is exactly between 23 and 24 hours away
        if timedelta(hours=23) <= time_until_event <= timedelta(hours=24):
            registrations = Registration.query.filter_by(event_id=event.event_id, status='registered').all()
            for reg in registrations:
                _send_email(
                    subject=f"Reminder: {event.event_name} is Tomorrow!",
                    recipient=reg.user.email,
                    template="reminder",
                    user=reg.user,
                    event=event,
                    time_remaining=time_until_event
                )
