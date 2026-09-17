from flask import url_for, redirect, render_template, flash, Blueprint, request
from flask_login import login_required
from app import db
from app.models import Payment, Lease

payments_bp=Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/')
@login_required
def list_payment():
    payments=Payment.query.order_by(Payment.rent_due_date.desc()).all()
    return render_template('payments/list.html', payments=payments)

@payments_bp.route('/new', methods=['POST', 'GET'])
@login_required
def add_payment():
    