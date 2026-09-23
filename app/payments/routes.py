from flask import url_for, redirect, render_template, flash, Blueprint, request
from flask_login import login_required
from app import db
from app.models import Payment, Lease

payments_bp=Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/')
@login_required
def list_payments():
    payments=Payment.query.order_by(Payment.due_date.desc()).all()
    return render_template('payments/list.html', payments=payments)

@payments_bp.route('/new', methods=['POST', 'GET'])
@login_required
def add_payment():
    if request.method=='POST':
        payment=Payment(
            lease_id=request.form['lease_id'],
            due_date=request.form['due_date'],
            amount=request.form['amount'],
            memo=request.form['memo'],
            pay_type=request.form['pay_type'],
            status=request.form['status']
        )

        db.session.add(payment)
        db.session.commit()
        flash('Payment added successfully')
        return redirect(url_for('payments.list_payments'))
    leases=Lease.query.filter_by(status='active').order_by(Lease.id).all()
    return render_template('payments/form.html', payment=None, leases=leases)

@payments_bp.route('/<int:payment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_payment(payment_id):
    payment=Payment.query.get_or_404(payment_id)
    if request.method=='POST':
        payment.lease_id=request.form['lease_id']
        payment.due_date=request.form['due_date']
        payment.amount=request.form['amount']
        payment.memo=request.form['memo'] or None
        payment.pay_type=request.form['pay_type'] or None
        payment.status=request.form['status'] or 'pending'
        db.session.commit()
        flash('Payment updated sucessfully')
        return redirect(url_for('payments.list_payments'))
    leases=Lease.query.order_by(Lease.id).all()
    return render_template('payments/form.html', leases=leases, payment=payment)


@payments_bp.route('/<int:payment_id>/delete', methods=['POST'])
@login_required
def delete_payment(payment_id):
    payment=Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted.')
    return redirect(url_for('payments.list_payments')) 


