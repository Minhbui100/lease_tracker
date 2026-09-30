from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import login_required
from app.models import Lease, Payment, MaintenanceRequest

dashboard_bp=Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    active_leases=Lease.query.filter_by(status='active').count()
    late_payments=Payment.query.filter_by(status='late').count()
    pending_payments = Payment.query.filter_by(status='pending').count()
    open_tickets = MaintenanceRequest.query.filter(MaintenanceRequest.status != 'resolved').count()

    return render_template('dashboard/index.html',active_leases=active_leases, late_payments=late_payments, pending_payments=pending_payments, open_tickets=open_tickets)