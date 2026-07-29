from datetime import datetime
import logging
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models import Event, Registration
from app.exceptions import EventValidationError, EventNotFoundError, EventOperationError
from sqlalchemy.orm import joinedload, selectinload
from app.services import email_service

logger = logging.getLogger(__name__)

def validate_event_data(data):
    """Validates the raw dictionary of event data. Raises EventValidationError on failure."""
    title = data.get('title', '').strip()
    event_type = data.get('event_type', '').strip()
    description = data.get('description', '').strip()
    venue = data.get('venue', '').strip()
    organizer = data.get('organizer', '').strip()
    capacity = data.get('capacity')
    event_date_str = data.get('event_date')
    event_time_str = data.get('event_time')

    if not title or not event_type or not venue or not organizer or not capacity or not event_date_str or not event_time_str:
        raise EventValidationError('All required fields must be filled.')

    if len(title) > 150:
        raise EventValidationError('Title cannot exceed 150 characters.')

    if len(description) > 500:
        raise EventValidationError('Description cannot exceed 500 characters.')

    try:
        capacity = int(capacity)
    except (ValueError, TypeError):
        raise EventValidationError('Capacity must be a valid integer.')

    if capacity <= 0:
        raise EventValidationError('Capacity must be greater than 0.')

    try:
        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        raise EventValidationError('Invalid date format.')

    try:
        event_time = datetime.strptime(event_time_str, '%H:%M').time()
    except (ValueError, TypeError):
        try:
            event_time = datetime.strptime(event_time_str, '%H:%M:%S').time()
        except (ValueError, TypeError):
            raise EventValidationError('Invalid time format.')

    if event_date < datetime.now().date():
        raise EventValidationError('Event date cannot be in the past.')

    return {
        'event_name': title,
        'event_type': event_type,
        'description': description,
        'venue': venue,
        'organizer': organizer,
        'capacity': capacity,
        'event_date': event_date,
        'event_time': event_time
    }

def list_events(search=None, venue=None, organizer=None, date_str=None):
    """Returns a list of events filtered by the provided criteria."""
    query = Event.query.filter_by(is_cancelled=False)
    
    if search:
        query = query.filter(Event.event_name.ilike(f'%{search}%'))
    if venue:
        query = query.filter(Event.venue.ilike(f'%{venue}%'))
    if organizer:
        query = query.filter(Event.organizer.ilike(f'%{organizer}%'))
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(Event.event_date == filter_date)
        except ValueError:
            pass # Ignore invalid date format in search

    return query.options(selectinload(Event.registrations)).order_by(Event.event_date.asc(), Event.event_time.asc()).all()

def get_event_by_id(event_id):
    """Fetches an event by ID or raises EventNotFoundError."""
    event = Event.query.get(event_id)
    if not event:
        raise EventNotFoundError(f"Event {event_id} not found.")
    return event

def get_event_details_context(event_id, current_user):
    """Returns a dictionary containing the event and all metadata required by the view_event template."""
    event = get_event_by_id(event_id)
    
    registrations_count = Registration.query.filter_by(event_id=event_id, status='registered').count()
    available_seats = event.capacity - registrations_count
    is_full = available_seats <= 0
    is_past = event.event_date < datetime.now().date()
    
    registration = None
    is_registered = False
    if current_user and current_user.is_authenticated:
        registration = Registration.query.filter_by(user_id=current_user.user_id, event_id=event_id, status='registered').first()
        is_registered = registration is not None
        
    return {
        'event': event,
        'registrations_count': registrations_count,
        'available_seats': available_seats,
        'is_full': is_full,
        'is_past': is_past,
        'is_registered': is_registered,
        'registration': registration
    }

def create_event(data):
    """Creates a new event after validating the data. Commits the transaction."""
    valid_data = validate_event_data(data)
    new_event = Event(**valid_data)
    
    try:
        db.session.add(new_event)
        db.session.commit()
        return new_event
    except Exception as e:
        db.session.rollback()
        raise EventOperationError("An error occurred while creating the event.") from e

def update_event(event_id, data):
    """Updates an existing event after validating the data. Commits the transaction and triggers emails on change."""
    event = get_event_by_id(event_id)
    valid_data = validate_event_data(data)
    
    # Change detection
    changed_fields = {}
    venue_changed = False
    old_venue = event.venue
    
    # We care about tracking venue, date, time, and other major details for emails.
    if event.venue != valid_data['venue']:
        venue_changed = True
        
    if event.event_date != valid_data['event_date']:
        changed_fields['date'] = {'old': event.event_date.strftime('%B %d, %Y'), 'new': valid_data['event_date'].strftime('%B %d, %Y')}
        
    if event.event_time != valid_data['event_time']:
        changed_fields['time'] = {'old': event.event_time.strftime('%H:%M'), 'new': valid_data['event_time'].strftime('%H:%M')}
        
    if event.event_name != valid_data['event_name']:
        changed_fields['title'] = {'old': event.event_name, 'new': valid_data['event_name']}
        
    if event.event_type != valid_data['event_type']:
        changed_fields['event type'] = {'old': event.event_type, 'new': valid_data['event_type']}
        
    if event.description != valid_data['description']:
        changed_fields['description'] = {'old': event.description, 'new': valid_data['description']}
    
    for key, value in valid_data.items():
        setattr(event, key, value)
        
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise EventOperationError("An error occurred while updating the event.") from e
        
    # Trigger Emails (Post-commit)
    try:
        if venue_changed or changed_fields:
            registrations = Registration.query.filter_by(event_id=event_id, status='registered').options(joinedload(Registration.user)).all()
            for reg in registrations:
                if venue_changed:
                    email_service.send_venue_change_notification(reg.user, event, old_venue, valid_data['venue'])
                else:
                    email_service.send_event_update_notification(reg.user, event, changed_fields)
    except Exception as e:
        logger.exception(f"Failed post-commit email operations for event {event_id}: {e}")
                    
    return event

def delete_event(event_id):
    """
    Cancels an event softly by setting is_cancelled = True.
    """
    event = get_event_by_id(event_id)
    try:
        event.is_cancelled = True
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise EventOperationError("An error occurred while cancelling the event.") from e
        
    # Trigger cancellation emails
    try:
        registrations = Registration.query.filter_by(event_id=event_id, status='registered').options(joinedload(Registration.user)).all()
        for reg in registrations:
            email_service.send_event_cancellation_notification(reg.user, event)
    except Exception as e:
        logger.exception(f"Failed to send cancellation emails for event {event_id}: {e}")

def get_event_participants(event_id):
    """Fetches all registrations for an event, efficiently eager-loading the User data."""
    event = get_event_by_id(event_id)
    registrations = Registration.query.filter_by(event_id=event_id)\
                        .options(joinedload(Registration.user))\
                        .order_by(Registration.registration_date.desc())\
                        .all()
    return event, registrations
