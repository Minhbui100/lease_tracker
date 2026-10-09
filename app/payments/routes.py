from flask import url_for, redirect, render_template, flash, Blueprint, request
from flask_login import login_required
from app import db
from app.models import Payment, Lease, PAYMENT_CATEGORIES
from app.validation import FormValidator
from datetime import date
from decimal import Decimal

payments_bp=Blueprint('payments', __name__, url_prefix='/payments')

PAY_TYPES={'check', 'cash', 'zelle', 'bank transfer'}
PAYMENT_STATUSES={'pending', 'paid', 'late'}


def validate_payment_form(form, lease_query):
    """Returns (cleaned_data, errors) for the payment add/edit form."""
    v=FormValidator(form)
    data={
        'lease': v.record('lease_id', 'Lease', Lease, query=lease_query),
        'due_date': v.date('due_date', 'Due date', required=True, min_value=date(1900, 1, 1)),
        'amount': v.decimal('amount', 'Amount', required=True, min_value=Decimal('0.01'), max_value=Decimal('99999999.99')),
        'memo': v.string('memo', 'Memo', max_length=50),
        'pay_type': v.choice('pay_type', 'Pay type', PAY_TYPES),
        'status': v.choice('status', 'Status', PAYMENT_STATUSES, default='pending'),
        'category': v.choice('category', 'Category', set(PAYMENT_CATEGORIES), required=True),
    }
    if data['status']=='paid' and not data['pay_type'] and 'pay_type' not in v.errors:
        v.add_error('pay_type', 'Please select a pay type for a paid payment.')
    return data, v.errors


def apply_payment_data(payment, data):
    payment.lease_id=data['lease'].id
    payment.due_date=data['due_date']
    payment.amount=data['amount']
    payment.memo=data['memo']
    payment.pay_type=data['pay_type']
    payment.status=data['status']
    payment.category=data['category']


@payments_bp.route('/')
@login_required
def list_payments():
    payments=Payment.query.order_by(Payment.due_date.desc()).all()
    return render_template('payments/list.html', payments=payments)

@payments_bp.route('/new', methods=['POST', 'GET'])
@login_required
def add_payment():
    active_leases=Lease.query.filter_by(status='active')
    if request.method=='POST':
        data, errors=validate_payment_form(request.form, active_leases)
        if errors:
            return render_template('payments/form.html', payment=None, leases=active_leases.order_by(Lease.id).all(), errors=errors, payment_categories=PAYMENT_CATEGORIES), 400

        payment=Payment()
        apply_payment_data(payment, data)
        db.session.add(payment)
        db.session.commit()
        flash('Payment added successfully')
        return redirect(url_for('payments.list_payments'))
    return render_template('payments/form.html', payment=None, leases=active_leases.order_by(Lease.id).all(), errors={}, payment_categories=PAYMENT_CATEGORIES)

@payments_bp.route('/<int:payment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_payment(payment_id):
    payment=Payment.query.get_or_404(payment_id)
    leases=Lease.query.order_by(Lease.id).all()
    if request.method=='POST':
        data, errors=validate_payment_form(request.form, Lease.query)
        if errors:
            return render_template('payments/form.html', leases=leases, payment=payment, errors=errors, payment_categories=PAYMENT_CATEGORIES), 400

        apply_payment_data(payment, data)
        db.session.commit()
        flash('Payment updated successfully')
        return redirect(url_for('payments.list_payments'))
    return render_template('payments/form.html', leases=leases, payment=payment, errors={}, payment_categories=PAYMENT_CATEGORIES)


@payments_bp.route('/<int:payment_id>/delete', methods=['POST'])
@login_required
def delete_payment(payment_id):
    payment=Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted.')
    return redirect(url_for('payments.list_payments')) 
