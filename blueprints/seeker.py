from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Service, Booking, Review
from forms import BookingForm

seeker_bp = Blueprint('seeker', __name__)

@seeker_bp.route('/seeker/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'seeker':
        flash('Access denied', 'danger')
        return redirect(url_for('provider.dashboard'))

    bookings = Booking.query.filter_by(seeker_id=current_user.id).all()
    return render_template('seeker/dashboard.html', bookings=bookings)

@seeker_bp.route('/seeker/services')
@login_required
def services():
    if current_user.user_type != 'seeker':
        flash('Access denied', 'danger')
        return redirect(url_for('provider.dashboard'))

    category = request.args.get('category', 'all')
    search = request.args.get('search', '')

    query = Service.query
    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Service.title.ilike(f'%{search}%'))

    services = query.all()
    return render_template('seeker/services.html', 
                         services=services,
                         category=category,
                         search=search)

@seeker_bp.route('/seeker/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book_service(service_id):
    if current_user.user_type != 'seeker':
        flash('Access denied', 'danger')
        return redirect(url_for('provider.dashboard'))

    service = Service.query.get_or_404(service_id)
    form = BookingForm()

    if form.validate_on_submit():
        # Check if booking already exists
        existing_booking = Booking.query.filter_by(
            service_id=service_id,
            date=form.date.data,
            time_slot=form.time_slot.data
        ).first()

        if existing_booking:
            flash('This time slot is already booked', 'danger')
        else:
            booking = Booking(
                service_id=service_id,
                seeker_id=current_user.id,
                date=form.date.data,
                time_slot=form.time_slot.data
            )
            db.session.add(booking)
            db.session.commit()
            flash('Booking request submitted!', 'success')
            return redirect(url_for('seeker.dashboard'))

    return render_template('seeker/book_service.html', 
                         service=service, 
                         form=form)

@seeker_bp.route('/seeker/review', methods=['POST'])
@login_required
def submit_review():
    if current_user.user_type != 'seeker':
        return jsonify({'error': 'Access denied'}), 403

    booking_id = request.form.get('booking_id')
    rating = request.form.get('rating')
    review_text = request.form.get('review_text')

    if not all([booking_id, rating]):
        return jsonify({'error': 'Missing required fields'}), 400

    booking = Booking.query.get_or_404(booking_id)

    # Verify this booking belongs to the current user
    if booking.seeker_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    # Check if review already exists
    if booking.review:
        return jsonify({'error': 'Review already submitted'}), 400

    # Create new review
    review = Review(
        booking_id=booking_id,
        service_id=booking.service_id,
        reviewer_id=current_user.id,
        provider_id=booking.service.provider_id,
        rating=int(rating),
        review_text=review_text
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        'message': 'Review submitted successfully',
        'rating': rating,
        'review_text': review_text
    })