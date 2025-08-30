from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Service, Booking, Availability
from forms import ServiceForm, AvailabilityForm
from datetime import datetime

provider_bp = Blueprint('provider', __name__)

@provider_bp.route('/provider/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'provider':
        flash('Access denied', 'danger')
        return redirect(url_for('seeker.dashboard'))

    services = Service.query.filter_by(provider_id=current_user.id).all()
    bookings = Booking.query.join(Service).filter(Service.provider_id == current_user.id).all()

    return render_template('provider/dashboard.html', 
                         services=services, 
                         bookings=bookings)

@provider_bp.route('/provider/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.user_type != 'provider':
        flash('Access denied', 'danger')
        return redirect(url_for('seeker.dashboard'))

    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            title=form.title.data,
            description=form.description.data,
            rate=form.rate.data,
            category=form.category.data,
            provider_id=current_user.id
        )
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('provider.dashboard'))

    services = Service.query.filter_by(provider_id=current_user.id).all()
    return render_template('provider/profile.html', 
                         form=form, 
                         services=services)

@provider_bp.route('/provider/availability', methods=['POST'])
@login_required
def add_availability():
    if current_user.user_type != 'provider':
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()

    # Convert string times to Time objects
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data['end_time'], '%H:%M').time()

    # Check if availability already exists for this day
    existing = Availability.query.filter_by(
        provider_id=current_user.id,
        day_of_week=int(data['day_of_week'])
    ).first()

    if existing:
        return jsonify({'error': 'Availability already exists for this day'}), 400

    availability = Availability(
        provider_id=current_user.id,
        day_of_week=int(data['day_of_week']),
        start_time=start_time,
        end_time=end_time,
        is_available=True
    )

    db.session.add(availability)
    db.session.commit()

    return jsonify({'success': True})

@provider_bp.route('/provider/availability/<int:availability_id>', methods=['DELETE'])
@login_required
def delete_availability(availability_id):
    if current_user.user_type != 'provider':
        return jsonify({'error': 'Access denied'}), 403

    availability = Availability.query.get_or_404(availability_id)
    if availability.provider_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    db.session.delete(availability)
    db.session.commit()

    return jsonify({'success': True})

@provider_bp.route('/provider/booking/<int:booking_id>/<string:action>')
@login_required
def manage_booking(booking_id, action):
    if current_user.user_type != 'provider':
        flash('Access denied', 'danger')
        return redirect(url_for('seeker.dashboard'))

    booking = Booking.query.get_or_404(booking_id)
    if booking.service.provider_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('provider.dashboard'))

    if action == 'approve':
        booking.status = 'approved'
        flash('Booking approved!', 'success')
    elif action == 'complete':
        booking.status = 'completed'
        flash('Booking marked as completed!', 'success')

    db.session.commit()
    return redirect(url_for('provider.dashboard'))

@provider_bp.route('/provider/service/<int:service_id>', methods=['DELETE'])
@login_required
def delete_service(service_id):
    if current_user.user_type != 'provider':
        return jsonify({'error': 'Access denied'}), 403

    service = Service.query.get_or_404(service_id)
    if service.provider_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
        
    # Notify users with pending/approved bookings
    affected_bookings = Booking.query.filter(
        Booking.service_id == service_id,
        Booking.status.in_(['pending', 'approved'])
    ).all()
    
    for booking in affected_bookings:
        flash(f'Service "{service.title}" has been canceled by the provider', 'warning')

    # Check if service has any completed bookings
    completed_bookings = Booking.query.filter_by(
        service_id=service_id, 
        status='completed'
    ).first()

    if completed_bookings:
        return jsonify({'error': 'Cannot delete service with completed bookings'}), 400

    try:
        # Delete only pending/approved bookings
        Booking.query.filter(
            Booking.service_id == service_id,
            Booking.status.in_(['pending', 'approved'])
        ).delete()
        
        # Then delete the service
        db.session.delete(service)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete service. Please try again.'}), 500