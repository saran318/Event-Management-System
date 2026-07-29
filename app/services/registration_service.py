from datetime import datetime
from app.extensions import db
from app.models import Event, Registration
from sqlalchemy.orm import joinedload
from app.exceptions import EventOperationError, EventNotFoundError
from app.services import email_service

def list_user_registrations(user_id):
    """Returns a list of all active registrations for a given user."""
    return Registration.query.options(joinedload(Registration.event)).filter_by(user_id=user_id, status='registered').order_by(Registration.registration_date.desc()).all()

def register_user_for_event(event_id, current_user):
    """
    Registers a user for an event, applying business rules.
    Sends a confirmation email on success.
    """
    event = Event.query.get(event_id)
    if not event:
        raise EventNotFoundError("Event not found.")

    if event.event_date < datetime.now().date():
        raise EventOperationError("Cannot register for past events.")
        
    existing_reg = Registration.query.filter_by(user_id=current_user.user_id, event_id=event_id).first()
    
    if existing_reg:
        if existing_reg.status == 'registered':
            raise EventOperationError("You are already registered for this event.")
        elif existing_reg.status == 'cancelled':
            registrations_count = Registration.query.filter_by(event_id=event_id, status='registered').count()
            if registrations_count >= event.capacity:
                raise EventOperationError("Sorry, this event is full.")
            
            existing_reg.status = 'registered'
            existing_reg.registration_date = datetime.utcnow()
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise EventOperationError("An error occurred. Please try again.") from e
                
            email_service.send_registration_confirmation(current_user, event)
            return existing_reg
                
    registrations_count = Registration.query.filter_by(event_id=event_id, status='registered').count()
    if registrations_count >= event.capacity:
        raise EventOperationError("Sorry, this event is full.")
        
    new_reg = Registration(user_id=current_user.user_id, event_id=event_id, status='registered')
    db.session.add(new_reg)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise EventOperationError("An error occurred during registration. Please try again.") from e
        
    email_service.send_registration_confirmation(current_user, event)
    return new_reg

def cancel_registration(registration_id, current_user):
    """Cancels a registration if the user owns it."""
    registration = Registration.query.get(registration_id)
    if not registration:
        raise EventNotFoundError("Registration not found.")
        
    if registration.user_id != current_user.user_id:
        raise EventOperationError("Unauthorized action.")
        
    if registration.status == 'cancelled':
        raise EventOperationError("Registration is already cancelled.")
        
    registration.status = 'cancelled'
    try:
        db.session.commit()
        return registration
    except Exception as e:
        db.session.rollback()
        raise EventOperationError("An error occurred while cancelling. Please try again.") from e
