from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from app.services import registration_service
from app.exceptions import EventOperationError, EventNotFoundError

registrations_bp = Blueprint('registrations', __name__)

@registrations_bp.route('/')
@login_required
def list_registrations():
    user_registrations = registration_service.list_user_registrations(current_user.user_id)
    return render_template('my_registrations.html', registrations=user_registrations)

@registrations_bp.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register(event_id):
    try:
        registration_service.register_user_for_event(event_id, current_user)
        flash('Registration successful!', 'success')
    except EventNotFoundError:
        abort(404)
    except EventOperationError as e:
        # Use warning for logical rejections (like already registered), danger for full event or past event. 
        # Just use warning as a safe default for business rules here.
        if "An error occurred" in str(e):
            flash(str(e), 'danger')
        else:
            flash(str(e), 'warning')
            
    return redirect(url_for('events.view_event', event_id=event_id))

@registrations_bp.route('/cancel/<int:registration_id>', methods=['POST'])
@login_required
def cancel_registration(registration_id):
    try:
        registration = registration_service.cancel_registration(registration_id, current_user)
        flash('Registration cancelled successfully.', 'success')
        
        referrer = request.referrer
        if referrer and '/events/' in referrer:
            return redirect(url_for('events.view_event', event_id=registration.event_id))
    except EventNotFoundError:
        abort(404)
    except EventOperationError as e:
        if "Unauthorized" in str(e):
            flash(str(e), 'danger')
        else:
            flash(str(e), 'warning')

    return redirect(url_for('registrations.list_registrations'))
