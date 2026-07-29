from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from app.decorators import admin_required
from app.services import event_service
from app.exceptions import EventValidationError, EventNotFoundError, EventOperationError

events_bp = Blueprint('events', __name__)

@events_bp.route('/')
def list_events():
    search = request.args.get('search', '').strip()
    venue = request.args.get('venue', '').strip()
    organizer = request.args.get('organizer', '').strip()
    date_str = request.args.get('date', '').strip()

    events = event_service.list_events(search, venue, organizer, date_str)
    return render_template('events.html', events=events)

@events_bp.route('/<int:event_id>')
def view_event(event_id):
    try:
        context = event_service.get_event_details_context(event_id, current_user)
        return render_template('event_details.html', **context)
    except EventNotFoundError:
        abort(404)

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    if request.method == 'POST':
        try:
            event_service.create_event(request.form)
            flash('Event Created Successfully', 'success')
            return redirect(url_for('events.list_events'))
        except EventValidationError as e:
            flash(str(e), 'danger')
            return redirect(url_for('events.create_event'))
        except EventOperationError as e:
            flash(str(e), 'danger')
            return redirect(url_for('events.create_event'))

    return render_template('create_event.html')

@events_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    try:
        event = event_service.get_event_by_id(event_id)
    except EventNotFoundError:
        abort(404)

    if request.method == 'POST':
        try:
            event_service.update_event(event_id, request.form)
            flash('Event Updated Successfully', 'success')
            return redirect(url_for('events.view_event', event_id=event_id))
        except EventValidationError as e:
            flash(str(e), 'danger')
            return redirect(url_for('events.edit_event', event_id=event_id))
        except EventOperationError as e:
            flash(str(e), 'danger')
            return redirect(url_for('events.edit_event', event_id=event_id))

    return render_template('edit_event.html', event=event)

@events_bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    try:
        event_service.delete_event(event_id)
        flash('Event Cancelled Successfully', 'success')
    except EventNotFoundError:
        abort(404)
    except EventOperationError as e:
        flash(str(e), 'danger')
        
    return redirect(url_for('events.list_events'))

@events_bp.route('/<int:event_id>/participants', methods=['GET'])
@login_required
@admin_required
def participants(event_id):
    try:
        event, registrations = event_service.get_event_participants(event_id)
        return render_template('participants.html', event=event, registrations=registrations)
    except EventNotFoundError:
        abort(404)
