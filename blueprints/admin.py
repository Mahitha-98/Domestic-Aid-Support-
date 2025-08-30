from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import User, Service, Booking

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    # Simple admin check - in production, use proper admin role
    if current_user.email != 'admin@example.com':
        flash('Access denied', 'danger')
        return redirect(url_for('seeker.dashboard'))
    
    users = User.query.all()
    services = Service.query.all()
    bookings = Booking.query.all()
    
    stats = {
        'total_users': len(users),
        'total_providers': len([u for u in users if u.user_type == 'provider']),
        'total_seekers': len([u for u in users if u.user_type == 'seeker']),
        'total_services': len(services),
        'total_bookings': len(bookings),
        'completed_bookings': len([b for b in bookings if b.status == 'completed'])
    }
    
    return render_template('admin/dashboard.html',
                         users=users,
                         services=services,
                         bookings=bookings,
                         stats=stats)

@admin_bp.route('/admin/user/<int:user_id>/toggle')
@login_required
def toggle_user(user_id):
    if current_user.email != 'admin@example.com':
        flash('Access denied', 'danger')
        return redirect(url_for('seeker.dashboard'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    flash(f'User {"activated" if user.is_active else "deactivated"}!', 'success')
    return redirect(url_for('admin.dashboard'))
